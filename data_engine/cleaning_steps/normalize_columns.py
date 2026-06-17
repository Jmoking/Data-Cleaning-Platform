def normalize_columns(df):
    cleaned_df = df.copy()
    cleaned_df.columns = [
        column.strip().lower().replace(" ", "_")
        for column in cleaned_df.columns
    ]
    return cleaned_df
