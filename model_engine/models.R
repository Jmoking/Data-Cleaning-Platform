quote_column <- function(column_name) {
  paste0("`", gsub("`", "``", column_name), "`")
}

soft_threshold <- function(value, penalty) {
  sign(value) * max(abs(value) - penalty, 0)
}

train_regularized_model <- function(train_data, target_column, feature_columns, model_type) {
  x <- as.matrix(train_data[feature_columns])
  y <- train_data[[target_column]]
  x_means <- colMeans(x)
  x_sds <- apply(x, 2, sd)
  x_sds[x_sds == 0] <- 1
  x_scaled <- scale(x, center = x_means, scale = x_sds)

  if (model_type == "ridge") {
    lambda <- 1
    design <- cbind("(Intercept)" = 1, x_scaled)
    penalty <- diag(ncol(design))
    penalty[1, 1] <- 0
    coefficients <- solve(t(design) %*% design + lambda * penalty, t(design) %*% y)

    return(list(
      model_type = "ridge",
      coefficients = as.numeric(coefficients),
      x_means = x_means,
      x_sds = x_sds
    ))
  }

  lambda <- 0.1
  y_mean <- mean(y)
  y_centered <- y - y_mean
  coefficients <- rep(0, ncol(x_scaled))

  for (iteration in seq_len(1000)) {
    previous_coefficients <- coefficients

    for (column_index in seq_along(coefficients)) {
      partial_residual <- y_centered - x_scaled[, -column_index, drop = FALSE] %*% coefficients[-column_index]
      raw_update <- sum(x_scaled[, column_index] * partial_residual) / nrow(x_scaled)
      coefficients[column_index] <- soft_threshold(raw_update, lambda)
    }

    if (max(abs(coefficients - previous_coefficients)) < 1e-7) {
      break
    }
  }

  list(
    model_type = "lasso",
    intercept = y_mean,
    coefficients = coefficients,
    x_means = x_means,
    x_sds = x_sds
  )
}

train_model <- function(train_data, target_column, feature_columns, model_type) {
  if (model_type == "linear") {
    formula_text <- paste(
      quote_column(target_column),
      "~",
      paste(sapply(feature_columns, quote_column), collapse = " + ")
    )

    return(list(
      model_type = "linear",
      fit = lm(as.formula(formula_text), data = train_data)
    ))
  }

  train_regularized_model(train_data, target_column, feature_columns, model_type)
}

predict_regularized_model <- function(model, test_data, feature_columns) {
  x <- as.matrix(test_data[feature_columns])
  x_scaled <- scale(x, center = model$x_means, scale = model$x_sds)

  if (model$model_type == "ridge") {
    design <- cbind("(Intercept)" = 1, x_scaled)
    return(as.numeric(design %*% model$coefficients))
  }

  as.numeric(model$intercept + x_scaled %*% model$coefficients)
}

predict_model <- function(model, test_data, feature_columns) {
  if (model$model_type == "linear") {
    return(as.numeric(predict(model$fit, newdata = test_data)))
  }

  predict_regularized_model(model, test_data, feature_columns)
}

predict_with_model <- function(train_data, test_data, target_column, feature_columns, model_type) {
  model <- train_model(train_data, target_column, feature_columns, model_type)
  predict_model(model, test_data, feature_columns)
}

get_model_parameters <- function(model, feature_columns) {
  if (model$model_type == "linear") {
    coefficients <- coef(model$fit)
    names(coefficients)[names(coefficients) == "(Intercept)"] <- "intercept"
    return(coefficients)
  }

  if (model$model_type == "ridge") {
    scaled_intercept <- model$coefficients[[1]]
    scaled_coefficients <- model$coefficients[-1]
  } else {
    scaled_intercept <- model$intercept
    scaled_coefficients <- model$coefficients
  }

  original_coefficients <- scaled_coefficients / model$x_sds
  original_intercept <- scaled_intercept - sum(scaled_coefficients * model$x_means / model$x_sds)
  parameters <- c(intercept = original_intercept, original_coefficients)
  names(parameters) <- c("intercept", feature_columns)
  parameters
}
