import os
import pandas as pd


def process_uploaded_file(file, upload_folder):
    """
    Validates, saves and reads the uploaded CSV file.

    Returns:
        success (bool)
        data (dict)
    """

    if not file.filename.endswith(".csv"):
        return False, {"error": "Please upload a CSV file."}

    filepath = os.path.join(upload_folder, file.filename)

    file.save(filepath)

    df = pd.read_csv(filepath)

    rows, columns = df.shape

    return True, {
        "rows": rows,
        "columns": columns,
        "filepath": filepath,
        "dataframe": df
    }