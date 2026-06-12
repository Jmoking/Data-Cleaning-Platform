args <- commandArgs(trailingOnly = FALSE)
file_arg <- "--file="
script_path <- sub(file_arg, "", args[grep(file_arg, args)])
script_dir <- dirname(normalizePath(script_path))

source(file.path(script_dir, "models.R"))

args <- commandArgs(trailingOnly = TRUE)

if (length(args) < 3) {
  stop("Usage: Rscript predict_with_saved_model.R <model_path> <input_csv_path> <output_csv_path>")
}

model_path <- args[[1]]
input_csv_path <- args[[2]]
output_csv_path <- args[[3]]

model_bundle <- readRDS(model_path)
new_data <- read.csv(input_csv_path, check.names = FALSE)
feature_columns <- model_bundle$feature_columns
target_column <- model_bundle$target_column
missing_columns <- setdiff(feature_columns, names(new_data))

if (length(missing_columns) > 0) {
  stop(paste("Prediction file is missing X variables:", paste(missing_columns, collapse = ", ")))
}

non_numeric_features <- feature_columns[!sapply(new_data[feature_columns], is.numeric)]

if (length(non_numeric_features) > 0) {
  stop(paste("Prediction X variables must be numeric:", paste(non_numeric_features, collapse = ", ")))
}

prediction_column <- paste0("predicted_", target_column)
new_data[[prediction_column]] <- predict_model(
  model_bundle$model,
  new_data,
  feature_columns
)

write.csv(new_data, output_csv_path, row.names = FALSE)
cat(paste0("{\"prediction_column\":\"", prediction_column, "\"}"))
