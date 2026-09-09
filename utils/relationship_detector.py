import pandas as pd


def get_correlation_strength(correlation):
    """
    Determine the strength of a correlation.

    Parameters:
        correlation (float):
            Pearson correlation coefficient.

    Returns:
        str: Correlation strength.
    """

    absolute_correlation = abs(correlation)

    if absolute_correlation >= 0.9:

        return "very strong"

    elif absolute_correlation >= 0.7:

        return "strong"

    elif absolute_correlation >= 0.5:

        return "moderate"

    elif absolute_correlation >= 0.3:

        return "weak"

    else:

        return "very weak"


def detect_relationships(df):
    """
    Detect strong relationships between numerical columns
    using Pearson correlation.

    Returns:
        list: Information about detected relationships.
    """

    results = []

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    # Need at least two numeric columns
    if len(numeric_columns) < 2:

        return results

    correlation_matrix = df[
        numeric_columns
    ].corr()

    # Compare each unique pair of columns
    for i in range(len(numeric_columns)):

        for j in range(i + 1, len(numeric_columns)):

            column_a = numeric_columns[i]

            column_b = numeric_columns[j]

            correlation = correlation_matrix.loc[
                column_a,
                column_b
            ]

            # Skip if correlation cannot be calculated
            if pd.isna(correlation):

                continue

            # Only keep strong relationships
            if abs(correlation) >= 0.7:

                if correlation > 0:

                    relationship = "positive"

                else:

                    relationship = "negative"

                strength = get_correlation_strength(
                    correlation
                )

                results.append({

                    "column_a": column_a,

                    "column_b": column_b,

                    "correlation": correlation,

                    "relationship": relationship,

                    "strength": strength

                })

    return results

def generate_relationship_findings(relationships):
    """
    Convert detected relationships into factual,
    human-readable findings.

    Parameters:
        relationships (list):
            Relationship results calculated by Python.

    Returns:
        list: Factual relationship findings.
    """

    findings = []

    for relationship in relationships:

        column_a = relationship["column_a"]

        column_b = relationship["column_b"]

        correlation = relationship["correlation"]

        direction = relationship["relationship"]

        strength = relationship["strength"]

        finding = (
            f"{column_a} and {column_b} show a "
            f"{strength} {direction} correlation "
            f"with a correlation coefficient of "
            f"{correlation:.2f}."
        )

        findings.append(finding)

    return findings