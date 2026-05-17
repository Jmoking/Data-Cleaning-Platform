import pandas as pd


def read_file(file_path):
    # Reade .csv or .xlsx or .xls file in to a dataframe
    
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)

    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return pd.read_excel(file_path)

    raise ValueError("Unsupported file type. Please use CSV or Excel.")