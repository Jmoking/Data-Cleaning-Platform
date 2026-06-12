run_evaluation <- function(model_data, train_index, test_index, target_column, feature_columns, model_type) {
  train_data <- model_data[train_index, ]
  test_data <- model_data[test_index, ]
  predictions <- predict_with_model(train_data, test_data, target_column, feature_columns, model_type)
  metrics <- calculate_metrics(test_data[[target_column]], predictions)

  list(
    train_rows = nrow(train_data),
    test_rows = nrow(test_data),
    rmse = metrics$rmse,
    mae = metrics$mae,
    r_squared = metrics$r_squared
  )
}

run_holdout_validation <- function(model_data, target_column, feature_columns, model_type) {
  train_size <- floor(0.8 * nrow(model_data))
  train_index <- sample(seq_len(nrow(model_data)), size = train_size)
  test_index <- setdiff(seq_len(nrow(model_data)), train_index)

  run_evaluation(model_data, train_index, test_index, target_column, feature_columns, model_type)
}

run_kfold_validation <- function(model_data, target_column, feature_columns, model_type, k_folds) {
  if (is.na(k_folds) || k_folds < 2) {
    stop("K-Fold validation needs at least 2 folds.")
  }

  if (k_folds > nrow(model_data)) {
    stop("K-Fold count cannot be larger than the number of model rows.")
  }

  shuffled_indices <- sample(seq_len(nrow(model_data)))
  folds <- split(shuffled_indices, rep(seq_len(k_folds), length.out = nrow(model_data)))

  lapply(folds, function(test_index) {
    train_index <- setdiff(seq_len(nrow(model_data)), test_index)
    run_evaluation(model_data, train_index, test_index, target_column, feature_columns, model_type)
  })
}
