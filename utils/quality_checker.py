import pandas as pd


def generate_quality_report(df):
    """
    Generate a complete data quality report.
    """

    # Missing values
    missing_values = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    # Empty columns
    empty_columns = [
        column
        for column in df.columns
        if df[column].isnull().all()
    ]

    # Basic statistics
    statistics = (
        df.describe(include="all")
        .fillna("-")
        .to_html(
            classes="table table-bordered table-striped",
            border=0
        )
    )

    # Dataset health
    issues = total_missing + duplicate_rows + len(empty_columns)

    if issues == 0:
        health = "Excellent"
    elif issues < 10:
        health = "Good"
    elif issues < 50:
        health = "Needs Cleaning"
    else:
        health = "Poor"

    # Human-friendly observations
    observations = []

    if total_missing == 0:
        observations.append("No missing values were found.")
    else:
        observations.append(
            f"The dataset contains {total_missing} missing value(s)."
        )

    if duplicate_rows == 0:
        observations.append("No duplicate rows were detected.")
    else:
        observations.append(
            f"The dataset contains {duplicate_rows} duplicate row(s)."
        )

    if len(empty_columns) == 0:
        observations.append("No completely empty columns were found.")
    else:
        observations.append(
            f"{len(empty_columns)} completely empty column(s) were detected."
        )

    report = {
        "health": health,
        "missing_values": missing_values,
        "total_missing": total_missing,
        "duplicate_rows": duplicate_rows,
        "empty_columns": empty_columns,
        "statistics": statistics,
        "observations": observations
    }

    return report