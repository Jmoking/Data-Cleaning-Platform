import pandas as pd


def analyse_data(df):

    analysis = {}

    # Basic statistics for numeric columns
    analysis["summary_statistics"] = (
        df.describe()
        .to_dict()
    )

    # Correlation between numeric columns
    numeric_df = df.select_dtypes(include="number")

    if len(numeric_df.columns) >= 2:
        analysis["correlation"] = (
            numeric_df.corr()
            .to_dict()
        )

    return analysis