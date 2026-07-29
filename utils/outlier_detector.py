import pandas as pd


def detect_outliers(df):
    """
    Detect outliers in all numeric columns using the IQR method.

    Returns:
        list: Information about detected outliers and
        the statistical evidence used to detect them.
    """

    results = []

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        values = df[column].dropna()

        # Skip columns with too few values
        if len(values) < 4:
            continue

        # Calculate quartiles
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        # Calculate IQR
        iqr = q3 - q1

        # Calculate outlier boundaries
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        # Find outliers
        outliers = values[
            (values < lower) |
            (values > upper)
        ]

        # Only store columns that contain outliers
        if len(outliers) > 0:

            results.append({

                "column": column,

                "count": len(outliers),

                "values": outliers.tolist(),

                "q1": q1,

                "q3": q3,

                "iqr": iqr,

                "lower_bound": lower,

                "upper_bound": upper

            })

    return results


def explain_outliers(outliers):
    """
    Convert detected outliers into human-readable explanations.
    """

    explanations = []

    for item in outliers:

        column = item["column"]
        count = item["count"]
        values = item["values"]

        explanation = (
            f"{column} contains {count} unusual value(s). "
            f"The detected value(s) {values} appear "
            f"different from the majority of the dataset."
        )

        explanations.append(explanation)

    return explanations