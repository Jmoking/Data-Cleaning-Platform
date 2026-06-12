load_model_data <- function(csv_path, target_column, feature_columns) {
  if (length(feature_columns) == 0) {
    stop("Please select at least one X variable.")
  }

  data <- read.csv(csv_path, check.names = FALSE)
  selected_columns <- c(target_column, feature_columns)
  missing_columns <- setdiff(selected_columns, names(data))

  if (length(missing_columns) > 0) {
    stop(paste("Column not found:", paste(missing_columns, collapse = ", ")))
  }

  model_data <- na.omit(data[selected_columns])

  if (!is.numeric(model_data[[target_column]])) {
    stop("The predict Y column must be numeric.")
  }

  non_numeric_features <- feature_columns[!sapply(model_data[feature_columns], is.numeric)]

  if (length(non_numeric_features) > 0) {
    stop(paste("X variables must be numeric:", paste(non_numeric_features, collapse = ", ")))
  }

  if (nrow(model_data) < 5) {
    stop("Not enough rows to train and test the model.")
  }

  model_data
}
