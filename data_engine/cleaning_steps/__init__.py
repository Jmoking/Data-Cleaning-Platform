from .blank_to_missing import blank_to_missing
from .convert_numeric_text import convert_numeric_text
from .drop_duplicates import drop_duplicates
from .fill_missing_values import fill_missing_values
from .normalize_columns import normalize_columns
from .trim_text import trim_text


CLEANING_STEPS = {
    "drop_duplicates": {
        "label": "Remove duplicates",
        "description": "Remove repeated rows from the dataset.",
        "function": drop_duplicates,
    },
    "normalize_columns": {
        "label": "Normalize column names",
        "description": "Lowercase column names and replace spaces with underscores.",
        "function": normalize_columns,
    },
    "trim_text": {
        "label": "Trim text values",
        "description": "Remove extra spaces before and after text values.",
        "function": trim_text,
    },
    "blank_to_missing": {
        "label": "Blank cells as missing",
        "description": "Treat empty strings and pure spaces as missing values.",
        "function": blank_to_missing,
    },
    "convert_numeric_text": {
        "label": "Convert numeric text",
        "description": "Convert text columns that contain only numbers into numeric columns.",
        "function": convert_numeric_text,
    },
    "fill_missing_values": {
        "label": "Fill missing values",
        "description": "Fill numeric missing values with the median and text missing values with Unknown.",
        "function": fill_missing_values,
    },
}


DEFAULT_CLEANING_STEPS = list(CLEANING_STEPS.keys())
