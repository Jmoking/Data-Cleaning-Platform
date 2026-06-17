def fill_missing_values(df):
    cleaned_df = df.copy()

    for column in cleaned_df.select_dtypes(include="number").columns:
        median_value = cleaned_df[column].median()
        cleaned_df[column] = cleaned_df[column].fillna(median_value)

    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].fillna("Unknown")

    return cleaned_df
