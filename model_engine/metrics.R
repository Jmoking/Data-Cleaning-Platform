format_number <- function(value) {
  if (is.na(value) || is.nan(value) || is.infinite(value)) {
    "null"
  } else {
    format(value, scientific = FALSE, digits = 10)
  }
}

json_escape <- function(value) {
  value <- gsub("\\\\", "\\\\\\\\", value)
  gsub("\"", "\\\\\"", value)
}

format_string <- function(value) {
  paste0("\"", json_escape(value), "\"")
}

format_string_array <- function(values) {
  paste(format_string(values), collapse = ",")
}

format_named_numbers <- function(values) {
  paste(
    paste0(format_string(names(values)), ":", sapply(values, format_number)),
    collapse = ","
  )
}

calculate_metrics <- function(actual, predictions) {
  errors <- actual - predictions
  rmse <- sqrt(mean(errors ^ 2))
  mae <- mean(abs(errors))
  sse <- sum(errors ^ 2)
  sst <- sum((actual - mean(actual)) ^ 2)
  r_squared <- if (sst == 0) NA else 1 - (sse / sst)

  list(rmse = rmse, mae = mae, r_squared = r_squared)
}
