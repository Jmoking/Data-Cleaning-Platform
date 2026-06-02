import pandas as pd


def profile_data(df):
    profiled_df = df.replace(r"^\s*$", pd.NA, regex=True)

    # Create an empty dictionary to store the profiling result
    report = {}

    # Count total number of rows in the DataFrame
    report["rows"] = len(profiled_df)

    # Count total number of columns
    report["columns"] = len(profiled_df.columns)

    # Convert column names into a normal Python list
    report["column_names"] = list(profiled_df.columns)

    # Check missing values for each column
    #
    # df.isnull()
    # turns the table into True / False values
    # where True means the value is missing
    #
    # .sum()
    # counts how many missing values each column has
    #
    # .to_dict()
    # converts the pandas result into a normal dictionary
    report["missing_values"] = profiled_df.isnull().sum().to_dict()

    # Check duplicate rows
    #
    # df.duplicated()
    # returns True for duplicated rows
    #
    # .sum()
    # counts how many duplicated rows exist
    #
    # int()
    # converts pandas integer type into normal Python int
    report["duplicate_rows"] = int(profiled_df.duplicated().sum())

    # Store the data type of each column
    report["data_types"] = {
        column: str(dtype)
        for column, dtype in profiled_df.dtypes.items()
    }

    # Return the final profiling report
    return report
