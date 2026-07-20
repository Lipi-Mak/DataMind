import pandas as pd


def get_dataset_overview(df):
    """
    Generate a basic overview of the uploaded dataset.
    """

    overview = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "data_types": df.dtypes.astype(str).to_dict(),
        "memory_usage": round(df.memory_usage(deep=True).sum() / 1024, 2),
        "preview": df.head().to_html(classes="table table-bordered", index=False)
    }

    return overview