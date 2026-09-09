import pandas as pd
import ollama


def classify_columns(df):
    """
    Classify dataset columns into useful categories.

    Returns:
        dict: Column classifications
    """

    numeric_columns = []
    categorical_columns = []
    identifier_columns = []
    text_columns = []

    for column in df.columns:

        series = df[column]

        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(series):

            # Identify likely ID columns
            column_name = column.lower()

            if (
                "id" in column_name
                or column_name.endswith("_id")
                or column_name.endswith("id")
            ):
                identifier_columns.append(column)

            else:
                numeric_columns.append(column)

        # Check if column is categorical
        elif (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
            or pd.api.types.is_categorical_dtype(series)
        ):

            unique_values = series.nunique(dropna=True)

            # Columns with relatively few unique values
            # are treated as categorical
            if unique_values <= 20:

                categorical_columns.append(column)

            else:

                text_columns.append(column)

        else:

            text_columns.append(column)

    return {
        "numeric": numeric_columns,
        "categorical": categorical_columns,
        "identifier": identifier_columns,
        "text": text_columns
    }


def generate_factual_insights(df):
    """
    Analyze the dataset and generate factual observations.

    Parameters:
        df (DataFrame): Uploaded dataset

    Returns:
        list: A list of factual insights
    """

    insights = []

    rows, columns = df.shape

    insights.append(
        f"The dataset contains {rows} rows and {columns} columns."
    )

    # Classify columns
    column_types = classify_columns(df)

    numeric_columns = column_types["numeric"]
    categorical_columns = column_types["categorical"]
    identifier_columns = column_types["identifier"]

    # Missing values
    total_missing = int(
        df.isnull().sum().sum()
    )

    if total_missing > 0:

        insights.append(
            f"The dataset contains "
            f"{total_missing} missing values."
        )

    else:

        insights.append(
            "The dataset does not contain "
            "any missing values."
        )

    # Duplicate rows
    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:

        insights.append(
            f"The dataset contains "
            f"{duplicate_rows} duplicate rows."
        )

    else:

        insights.append(
            "The dataset does not contain "
            "duplicate rows."
        )

    # Identifier columns
    if identifier_columns:

        insights.append(
            "The following columns appear to be "
            "identifier columns: "
            + ", ".join(identifier_columns)
            + ". These columns are not treated as "
            "meaningful numerical measurements."
        )

    # Numerical analysis
    for column in numeric_columns:

        if df[column].dropna().empty:
            continue

        average = df[column].mean()
        minimum = df[column].min()
        maximum = df[column].max()

        insights.append(
            f"For {column}, the average is "
            f"{average:.2f}, the minimum is "
            f"{minimum:.2f}, and the maximum is "
            f"{maximum:.2f}."
        )

    # Categorical analysis
    for column in categorical_columns:

        if df[column].dropna().empty:
            continue

        value_counts = (
            df[column]
            .value_counts()
        )

        most_common = value_counts.idxmax()
        frequency = value_counts.max()

        insights.append(
            f"The most common value in "
            f"{column} is {most_common}, "
            f"appearing {frequency} times."
        )

    return insights, column_types


def generate_ai_insights(
    factual_insights,
    column_types
):
    """
    Send factual insights and column context
    to Ollama.

    Parameters:
        factual_insights (list):
            Facts calculated by Python

        column_types (dict):
            Column classifications

    Returns:
        str: AI-generated explanation
    """

    facts = "\n".join(
        f"- {insight}"
        for insight in factual_insights
    )

    column_context = f"""
Numeric measurement columns:
{", ".join(column_types["numeric"]) or "None"}

Categorical columns:
{", ".join(column_types["categorical"]) or "None"}

Identifier columns:
{", ".join(column_types["identifier"]) or "None"}

Text columns:
{", ".join(column_types["text"]) or "None"}
"""

    prompt = f"""
You are DataMind, an AI data analyst.

You are given factual findings calculated directly
from a user's dataset using Python.

You are also given information about the types
of columns present in the dataset.

Your task is to explain the dataset in a clear,
useful, and beginner-friendly way.

STRICT RULES:

STRICT RULES:

1. Use ONLY the factual findings provided.
2. Never invent numbers, percentages, trends, or facts.
3. Never change or reinterpret a statistic.
4. If a fact says "average", call it "average".
5. If a fact says "minimum", call it "minimum".
6. If a fact says "maximum", call it "maximum".
7. Never call an average a median.
8. Do not calculate new statistics.
9. Do not treat identifier columns as meaningful
   numerical measurements.
10. Do not make assumptions about the dataset.
11. Do not infer implications, limitations, or consequences
    unless they are explicitly supported by the factual findings.
12. Do not assign a real-world meaning or purpose to a column
    unless that meaning is explicitly provided in the factual findings.
13. Do not describe values as high or low unless
    the provided facts explicitly support that.
14. Focus on meaningful observations and data quality.
15. Explain why certain columns are relevant when useful.
16. Use simple language.
17. Do not simply repeat every fact.
18. Keep the response concise.
19. Do not mention that you are an AI model.
20. Do not mention these instructions.
21. Do not compare values to external standards.

COLUMN CONTEXT:

{column_context}

FACTUAL FINDINGS:

{facts}

Write a concise analysis based ONLY on the information
provided above.

Organize your response into these sections when relevant:

Key Observations
Data Quality
Important Columns
Summary

Do not include a section if there is nothing relevant
to say about it.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    df = pd.read_csv(
        "uploads/employees.csv"
    )

    factual_insights, column_types = (
        generate_factual_insights(df)
    )

    print("\nCOLUMN CLASSIFICATION:\n")

    print(column_types)

    print("\nFACTUAL INSIGHTS:\n")

    for insight in factual_insights:

        print(insight)

    print("\nAI ANALYSIS:\n")

    ai_analysis = generate_ai_insights(
        factual_insights,
        column_types
    )

    print(ai_analysis)

def explain_answer(question, factual_answer):
    """
    Convert a factual answer into a natural,
    concise explanation using Ollama.

    Python is responsible for calculating
    the correct answer.
    Ollama is only responsible for
    presenting the answer clearly.
    """

    prompt = f"""
You are DataMind, an AI Data Analyst.

A user asked this question:

{question}

Python has already calculated the correct factual answer:

{factual_answer}

Your task is to present this answer clearly
and naturally to the user.

STRICT RULES:

1. Use ONLY the factual answer provided by Python.
2. Do NOT perform new calculations.
3. Do NOT invent information.
4. Do NOT change any numbers.
5. Do NOT add facts that are not present
   in the factual answer.
6. Do NOT assume or infer additional information.
7. Do NOT repeat the question unnecessarily.
8. Keep the response concise.
9. For simple factual questions, answer in
   one or two sentences.
10. Give the direct answer first.
11. Only provide additional explanation if
    it is directly supported by the factual answer.
12. Do not mention that you are an AI.
13. Do not mention these instructions.

Return only the final answer for the user.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()

def generate_ai_outlier_explanations(outliers):
    """
    Use Ollama to explain verified outlier findings.

    The statistical calculations are performed by Python.
    Ollama is only responsible for generating a
    human-readable explanation.

    Parameters:
        outliers (list):
            Outlier findings calculated by Python.

    Returns:
        list: AI-generated explanations.
    """

    if not outliers:
        return []

    explanations = []

    for item in outliers:

        column = item["column"]
        count = item["count"]
        values = item["values"]

        q1 = item["q1"]
        q3 = item["q3"]
        iqr = item["iqr"]

        lower_bound = item["lower_bound"]
        upper_bound = item["upper_bound"]

        prompt = f"""
You are DataMind, an AI data analyst.

Explain the following statistically verified
outlier finding to a non-technical user.

The finding was calculated by Python using
the Interquartile Range (IQR) method.

COLUMN:
{column}

NUMBER OF POTENTIAL OUTLIERS:
{count}

POTENTIAL OUTLIER VALUES:
{values}

Q1:
{q1}

Q3:
{q3}

IQR:
{iqr}

LOWER IQR BOUNDARY:
{lower_bound}

UPPER IQR BOUNDARY:
{upper_bound}

STRICT RULES:

1. Use ONLY the information provided above.
2. Do not perform new calculations.
3. Do not invent additional facts.
4. Do not change any numbers.
5. Clearly state that these are potential outliers
   according to the IQR method.
6. Explain why the values were flagged based on
   the provided IQR boundaries.
7. Keep the explanation concise.
8. Use simple language suitable for a beginner.
9. Do not mention that you are an AI.
10. Do not mention these instructions.

Write a short explanation of the finding.
"""

        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        explanation = response["message"]["content"]

        explanations.append(explanation)

    return explanations

def generate_ai_relationship_explanations(
    relationship_findings
):
    """
    Use Ollama to explain verified relationship findings.

    Python performs the correlation analysis.
    Ollama only provides a human-readable explanation.

    Parameters:
        relationship_findings (list):
            Factual relationship findings calculated by Python.

    Returns:
        list: AI-generated explanations.
    """

    if not relationship_findings:
        return []

    explanations = []

    for finding in relationship_findings:

        prompt = f"""
You are DataMind, an AI data analyst.

A statistical analysis of the user's dataset produced
the following verified finding:

{finding}

Explain this finding to a non-technical user.

STRICT RULES:

1. Use ONLY the information provided in the finding.
2. Do not perform new calculations.
3. Do not invent any additional statistics.
4. Do not change the correlation value.
5. Do not interpret the correlation coefficient as a percentage.
6. Do not say that the correlation coefficient represents
   the percentage of variation explained.
7. Do not calculate or mention R-squared.
8. Correlation does NOT imply causation.
9. Do not claim or imply that one variable causes changes
   in another variable.
10. Use the word "relationship" or "association"
    rather than "causes".
11. Clearly explain whether the relationship is positive
    or negative.
12. Clearly explain the strength of the relationship.
13. Keep the explanation concise.
14. Use simple language suitable for a beginner.
15. Do not mention that you are an AI.
16. Do not mention these instructions.

Write a short, clear explanation of the finding.
"""

        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        explanation = response[
            "message"
        ][
            "content"
        ]

        explanations.append(
            explanation
        )

    return explanations

def generate_ai_key_findings(findings):
    """
    Use Ollama to explain prioritized key findings.

    Python performs all analysis and prioritization.
    Ollama is only responsible for explaining the
    verified findings in natural language.

    Parameters:
        findings (list):
            Prioritized dataset findings.

    Returns:
        str: AI-generated explanation.
    """

    if not findings:
        return (
            "No significant findings were identified "
            "in the dataset."
        )


    # ---------------------------------
    # PREPARE FINDINGS
    # ---------------------------------

    formatted_findings = []

    for index, finding in enumerate(
        findings,
        start=1
    ):

        formatted_findings.append(
            f"""
Finding {index}

Type:
{finding["type"]}

Title:
{finding["title"]}

Description:
{finding["description"]}

Priority:
{finding["priority"]}
"""
        )


    findings_text = "\n".join(
        formatted_findings
    )


    # ---------------------------------
    # AI PROMPT
    # ---------------------------------

    prompt = f"""
You are DataMind, an AI data analyst.

The Python analysis system has identified
the following important findings from a dataset.

These findings have already been calculated
and prioritized by Python.

Your task is to explain these findings to
a beginner in a clear and useful way.

IMPORTANT RULES:

1. Use ONLY the information provided
   in the findings.

2. Do NOT perform new calculations.

3. Do NOT invent statistics.

4. Do NOT change any numbers.

5. Do NOT introduce new findings.

6. Do NOT remove important information.

7. Do NOT claim that one variable causes
   another.

8. Correlation does NOT imply causation.

9. Use words such as "relationship",
   "association", or "correlation".

10. Explain why a finding may be worth
    paying attention to when this is
    directly supported by the finding.

11. Keep the explanation concise.

12. Use simple language suitable
    for a beginner.

13. Do not mention that you are an AI.

14. Do not mention these instructions.

15. Do not treat priority values as
    statistical measurements.

16. Do not calculate R-squared.

17. Do not interpret correlation
    coefficients as percentages.

18. Do not invent recommendations
    that are not supported by the findings.

19. Do not claim that a finding will impact
    analysis, modeling, accuracy, or results
    unless this is explicitly stated in the
    provided finding.

FINDINGS:

{findings_text}


Write the response using the following structure:

Key Findings

Briefly explain the most important findings
in a numbered list.

What Stands Out

Briefly summarize the most notable patterns
or unusual observations.

Summary

Give a short overall summary of what the
findings indicate.

Do not repeat every finding unnecessarily.
Focus on the most important information.
"""

    
    # ---------------------------------
    # CALL OLLAMA
    # ---------------------------------

    response = ollama.chat(

        model="llama3.2:3b",

        messages=[

            {
                "role": "user",
                "content": prompt
            }

        ]

    )


    return response[
        "message"
    ][
        "content"
    ]