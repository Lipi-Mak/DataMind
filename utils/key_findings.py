def prioritize_finding(finding):
    """
    Assign a priority score to a finding.

    Higher scores indicate findings that are
    potentially more important to investigate.

    Returns:
        int: Priority score
    """

    finding_type = finding["type"]

    title = finding["title"].lower()


    # ---------------------------------
    # DATA QUALITY
    # ---------------------------------

    if finding_type == "Data Quality":

        if "empty" in title:

            return 5

        if "missing" in title:

            return 4

        if "duplicate" in title:

            return 3


    # ---------------------------------
    # OUTLIERS
    # ---------------------------------

    if finding_type == "Unusual Data":

        return 5


    # ---------------------------------
    # RELATIONSHIPS
    # ---------------------------------

    if finding_type == "Relationship":

        return 4


    # ---------------------------------
    # CATEGORIES
    # ---------------------------------

    if finding_type == "Category":

        return 2


    # ---------------------------------
    # DEFAULT
    # ---------------------------------

    return 1


def get_top_findings(
    findings,
    limit=5
):
    """
    Return the most important findings.

    Parameters:
        findings (list):
            Prioritized findings.

        limit (int):
            Maximum number of findings to return.

    Returns:
        list: Top prioritized findings.
    """

    return findings[:limit]



def generate_key_findings(
    quality_report,
    outliers,
    relationship_findings,
    factual_insights
):
    """
    Combine verified analysis results into
    a unified list of important dataset findings.

    All findings are generated from Python-calculated
    results. No AI is used in this function.

    Returns:
        list: Key findings about the dataset.
    """

    findings = []


    # =================================
    # DATA QUALITY FINDINGS
    # =================================

    total_missing = quality_report.get(
        "total_missing",
        0
    )

    duplicate_rows = quality_report.get(
        "duplicate_rows",
        0
    )

    empty_columns = quality_report.get(
        "empty_columns",
        []
    )


    # Missing values

    if total_missing > 0:

        findings.append({
            "type": "Data Quality",

            "title": "Missing Values",

            "description": (
                f"The dataset contains "
                f"{total_missing} missing value(s)."
            )
        })


    # Duplicate rows

    if duplicate_rows > 0:

        findings.append({
            "type": "Data Quality",

            "title": "Duplicate Rows",

            "description": (
                f"The dataset contains "
                f"{duplicate_rows} duplicate row(s)."
            )
        })


    # Completely empty columns

    if empty_columns:

        findings.append({
            "type": "Data Quality",

            "title": "Empty Columns",

            "description": (
                f"The following columns are "
                f"completely empty: "
                f"{', '.join(empty_columns)}."
            )
        })


    # =================================
    # OUTLIER FINDINGS
    # =================================

    for outlier in outliers:

        column = outlier["column"]

        count = outlier["count"]

        values = outlier["values"]


        findings.append({

            "type": "Unusual Data",

            "title": (
                f"Potential Outlier in {column}"
            ),

            "description": (
                f"{count} unusual value(s) were "
                f"detected in {column}: "
                f"{values}."
            )

        })


    # =================================
    # RELATIONSHIP FINDINGS
    # =================================

    for relationship in relationship_findings:

        column_a = relationship["column_a"]

        column_b = relationship["column_b"]

        correlation = float(
            relationship["correlation"]
        )

        relationship_type = (
            relationship["relationship"]
        )

        strength = relationship["strength"]


        description = (
            f"{column_a} and {column_b} show a "
            f"{strength} {relationship_type} "
            f"relationship with a correlation "
            f"coefficient of {correlation:.2f}."
        )


        findings.append({

            "type": "Relationship",

            "title": (
                f"{column_a} and {column_b}"
            ),

            "description": description

        })


    # =================================
    # CATEGORICAL FINDINGS
    # =================================

    for insight in factual_insights:

        if "most common value" in insight.lower():

            findings.append({

                "type": "Category",

                "title": "Most Common Category",

                "description": insight

            })


    # ---------------------------------
    # ASSIGN PRIORITY
    # ---------------------------------

    for finding in findings:

        finding["priority"] = (
            prioritize_finding(finding)
        )


    # ---------------------------------
    # SORT BY PRIORITY
    # ---------------------------------

    findings.sort(

        key=lambda finding:
            finding["priority"],

        reverse=True

    )


    return findings