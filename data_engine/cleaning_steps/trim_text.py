def trim_text(df):
    cleaned_df = df.copy()

    for column in cleaned_df.select_dtypes(include="object").columns:
        cleaned_df[column] = cleaned_df[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    return cleaned_df
