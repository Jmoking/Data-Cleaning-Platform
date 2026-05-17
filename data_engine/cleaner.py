def clean_data(df):
    cleaned_df = df.copy()

    # Remove duplicate rows
    cleaned_df = cleaned_df.drop_duplicates()

    # Clean column names
    cleaned_df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in cleaned_df.columns
    ]

    # Strip whitespace from text columns
    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].str.strip()

    # Fill missing values in numeric columns with median
    for column in cleaned_df.select_dtypes(include="number").columns:
        median_value = cleaned_df[column].median()
        cleaned_df[column] = cleaned_df[column].fillna(median_value)

    # Fill missing values in text columns with "Unknown"
    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].fillna("Unknown")

    return cleaned_df