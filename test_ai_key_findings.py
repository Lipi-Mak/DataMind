from utils.key_findings import (
    generate_key_findings,
    get_top_findings
)

from utils.insight_generator import (
    generate_ai_key_findings
)


# ---------------------------------
# MOCK QUALITY REPORT
# ---------------------------------

quality_report = {

    "total_missing": 2,

    "duplicate_rows": 1,

    "empty_columns": []

}


# ---------------------------------
# MOCK OUTLIERS
# ---------------------------------

outliers = [

    {

        "column": "Salary",

        "count": 1,

        "values": [250000]

    }

]


# ---------------------------------
# MOCK RELATIONSHIPS
# ---------------------------------

relationship_findings = [

    "Experience and Salary show a very strong "
    "positive correlation with a correlation "
    "coefficient of 0.98."

]


# ---------------------------------
# MOCK FACTUAL INSIGHTS
# ---------------------------------

factual_insights = [

    "The dataset contains 10 rows and 6 columns.",

    "The most common value in Department is IT, "
    "appearing 4 times."

]


# ---------------------------------
# GENERATE FINDINGS
# ---------------------------------

findings = generate_key_findings(

    quality_report,

    outliers,

    relationship_findings,

    factual_insights

)


# ---------------------------------
# GET TOP FINDINGS
# ---------------------------------

top_findings = get_top_findings(

    findings,

    limit=5

)


# ---------------------------------
# GENERATE AI EXPLANATION
# ---------------------------------

print(
    "\nGenerating AI Key Findings...\n"
)


ai_explanation = generate_ai_key_findings(

    top_findings

)


# ---------------------------------
# PRINT RESULT
# ---------------------------------

print(
    "\nDataMind AI Key Findings:\n"
)

print(
    ai_explanation
)