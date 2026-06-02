import pandas as pd
from pathlib import Path


def read_file(file_path):
    # Reade .csv or .xlsx or .xls file in to a dataframe
    file_path = Path(file_path)
    file_extension = file_path.suffix.lower()
    
    if file_extension == ".csv":
        return pd.read_csv(file_path)

    if file_extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    raise ValueError("Unsupported file type. Please use CSV or Excel.")
