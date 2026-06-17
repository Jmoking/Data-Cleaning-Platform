import pandas as pd


def blank_to_missing(df):
    return df.replace(r"^\s*$", pd.NA, regex=True)
