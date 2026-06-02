import pandas as pd


def clean_data(df):
    cleaned_df = df.copy()

    # Remove duplicate rows
    cleaned_df = cleaned_df.drop_duplicates()

    # Clean column names
    cleaned_df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in cleaned_df.columns
    ]

    # Strip whitespace from text columns and treat blank values as missing
    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        cleaned_df[column] = cleaned_df[column].replace("", pd.NA)

    # Convert text columns that contain only numbers into numeric columns
    for column in cleaned_df.select_dtypes(include="object").columns:
        converted_column = pd.to_numeric(cleaned_df[column], errors="coerce")
        non_missing_values = cleaned_df[column].notna()

        if non_missing_values.any() and converted_column[non_missing_values].notna().all():
            cleaned_df[column] = converted_column

    # Fill missing values in numeric columns with median
    for column in cleaned_df.select_dtypes(include="number").columns:
        median_value = cleaned_df[column].median()
        cleaned_df[column] = cleaned_df[column].fillna(median_value)

    # Fill missing values in text columns with "Unknown"
    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].fillna("Unknown")

    return cleaned_df
