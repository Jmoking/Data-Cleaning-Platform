import pandas as pd


def convert_numeric_text(df):
    cleaned_df = df.copy()

    for column in cleaned_df.select_dtypes(include="object").columns:
        converted_column = pd.to_numeric(cleaned_df[column], errors="coerce")
        non_missing_values = cleaned_df[column].notna()

        if non_missing_values.any() and converted_column[non_missing_values].notna().all():
            cleaned_df[column] = converted_column

    return cleaned_df
