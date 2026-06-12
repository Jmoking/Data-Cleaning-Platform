args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_path <- sub(file_arg, "", args[grep(file_arg, args)])
script_dir <- dirname(normalizePath(script_path))

source(file.path(script_dir, "metrics.R"))
source(file.path(script_dir, "data_prep.R"))
source(file.path(script_dir, "models.R"))
source(file.path(script_dir, "validation.R"))

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 3) {
  stop("Usage: Rscript linear_regression.R <csv_path> <target_column> <feature_columns> [model_type] [validation_method] [k_folds] [model_output_path]")
}

csv_path <- args[[1]]
target_column <- args[[2]]
feature_columns <- strsplit(args[[3]], ",", fixed = TRUE)[[1]]
feature_columns <- feature_columns[feature_columns != ""]
model_type <- ifelse(length(args) >= 4, args[[4]], "linear")
validation_method <- ifelse(length(args) >= 5, args[[5]], "holdout")
k_folds <- ifelse(length(args) >= 6, as.integer(args[[6]]), 5)
model_output_path <- ifelse(length(args) >= 7, args[[7]], "")

allowed_model_types <- c("linear", "ridge", "lasso")
allowed_validation_methods <- c("holdout", "kfold")

if (!(model_type %in% allowed_model_types)) {
  stop("Model type must be one of: linear, ridge, lasso.")
}

if (!(validation_method %in% allowed_validation_methods)) {
  stop("Validation method must be one of: holdout, kfold.")
}

model_data <- load_model_data(csv_path, target_column, feature_columns)

set.seed(42)
final_model <- train_model(model_data, target_column, feature_columns, model_type)
model_parameters <- get_model_parameters(final_model, feature_columns)

if (model_output_path != "") {
  saveRDS(
    list(
      model = final_model,
      model_type = model_type,
      target_column = target_column,
      feature_columns = feature_columns,
      parameters = model_parameters
    ),
    model_output_path
  )
}

if (validation_method == "holdout") {
  result <- run_holdout_validation(model_data, target_column, feature_columns, model_type)

  json <- paste0(
    "{",
    "\"model_type\":\"", model_type, "\",",
    "\"validation_method\":\"holdout\",",
    "\"target_column\":\"", target_column, "\",",
    "\"feature_columns\":[", format_string_array(feature_columns), "],",
    "\"parameters\":{", format_named_numbers(model_parameters), "},",
    "\"train_rows\":", result$train_rows, ",",
    "\"test_rows\":", result$test_rows, ",",
    "\"metrics\":{",
    "\"rmse\":", format_number(result$rmse), ",",
    "\"mae\":", format_number(result$mae), ",",
    "\"r_squared\":", format_number(result$r_squared),
    "}",
    "}"
  )
} else {
  fold_results <- run_kfold_validation(
    model_data,
    target_column,
    feature_columns,
    model_type,
    k_folds
  )

  json <- paste0(
    "{",
    "\"model_type\":\"", model_type, "\",",
    "\"validation_method\":\"kfold\",",
    "\"k_folds\":", k_folds, ",",
    "\"target_column\":\"", target_column, "\",",
    "\"feature_columns\":[", format_string_array(feature_columns), "],",
    "\"parameters\":{", format_named_numbers(model_parameters), "},",
    "\"average_train_rows\":", format_number(mean(sapply(fold_results, `[[`, "train_rows"))), ",",
    "\"average_test_rows\":", format_number(mean(sapply(fold_results, `[[`, "test_rows"))), ",",
    "\"metrics\":{",
    "\"rmse\":", format_number(mean(sapply(fold_results, `[[`, "rmse"))), ",",
    "\"mae\":", format_number(mean(sapply(fold_results, `[[`, "mae"))), ",",
    "\"r_squared\":", format_number(mean(sapply(fold_results, `[[`, "r_squared"), na.rm = TRUE)),
    "}",
    "}"
  )
}

cat(json)
