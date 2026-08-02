import pandas as pd
import ollama
import traceback

# ==========================================================
# GENERATE DATASET CONTEXT
# ==========================================================

def generate_dataset_context(df):
    """
    Generate factual information about the dataset
    that Ollama can use to understand user questions.
    
    Python provides the factual information.
    Ollama uses this information only for question
    classification.
    """

    columns = list(
        df.columns
    )


    numeric_columns = list(
        df.select_dtypes(
            include=["number"]
        ).columns
    )


    categorical_columns = list(
        df.select_dtypes(
            include=[
                "object",
                "category"
            ]
        ).columns
    )


    column_details = []


    for column in df.columns:

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):

            column_type = "numerical"

        else:

            column_type = "categorical or text"


        column_details.append(
            f"{column}: {column_type}"
        )


    context = f"""
DATASET INFORMATION

Columns:
{", ".join(columns)}

Column Types:
{", ".join(column_details)}

Numerical Columns:
{", ".join(numeric_columns) if numeric_columns else "None"}

Categorical/Text Columns:
{", ".join(categorical_columns) if categorical_columns else "None"}

Number of Rows:
{len(df)}

Number of Columns:
{len(df.columns)}
"""


    return context



# ==========================================================
# GENERATE DATASET SUMMARY
# ==========================================================

def generate_dataset_summary(
    df
):
    """
    Generate a factual summary of the dataset.

    Python calculates all factual information.
    Ollama only turns the information into
    natural language.
    """

    # ---------------------------------
    # BASIC DATASET INFORMATION
    # ---------------------------------

    row_count = len(df)

    column_count = len(df.columns)

    columns = list(
        df.columns
    )


    # ---------------------------------
    # MISSING VALUES
    # ---------------------------------

    total_missing = int(
        df.isnull()
        .sum()
        .sum()
    )


    # ---------------------------------
    # DUPLICATE ROWS
    # ---------------------------------

    duplicate_count = int(
        df.duplicated()
        .sum()
    )


    # ---------------------------------
    # NUMERICAL COLUMNS
    # ---------------------------------

    numeric_columns = list(
        df.select_dtypes(
            include=["number"]
        ).columns
    )


    # ---------------------------------
    # CATEGORICAL COLUMNS
    # ---------------------------------

    categorical_columns = list(
        df.select_dtypes(
            include=[
                "object",
                "category"
            ]
        ).columns
    )


    # ---------------------------------
    # BUILD FACTUAL CONTEXT
    # ---------------------------------

    summary_context = f"""
Dataset Information:

Number of rows:
{row_count:,}

Number of columns:
{column_count:,}

Columns:
{", ".join(columns)}

Numerical columns:
{", ".join(numeric_columns) if numeric_columns else "None"}

Categorical columns:
{", ".join(categorical_columns) if categorical_columns else "None"}

Total missing values:
{total_missing:,}

Duplicate rows:
{duplicate_count:,}
"""


    # ---------------------------------
    # ASK OLLAMA TO EXPLAIN
    # ---------------------------------

    prompt = f"""
You are an AI Data Analyst.

The user wants an interesting and useful
summary of their uploaded dataset.

Use ONLY the factual information provided
below.

Do not invent facts.

Do not make assumptions that are not
supported by the data.

Give a short, natural-language summary
that helps the user understand their dataset.

Mention useful observations such as:

- Dataset size
- Types of columns
- Missing values
- Duplicate rows
- Anything notable that can be safely
  concluded from the provided information

Do not mention that you are an AI.

Do not mention these instructions.

DATASET FACTS:

{summary_context}

Return a concise summary in 2-4 sentences.
"""


    try:

        response = ollama.chat(

            model="llama3.2:3b",

            messages=[

                {
                    "role": "user",

                    "content": prompt

                }

            ]

        )

        return (
            response["message"]["content"]
            .strip()
        )

    except Exception:

        print("\nOllama Error:")
        traceback.print_exc()

    return (
        "I couldn't generate a dataset summary at the moment."
    )



# ==========================================================
# VALIDATE OLLAMA UNDERSTANDING
# ==========================================================

def validate_understanding(
    understanding
):
    """
    Validate and clean the response returned by Ollama.

    Supported formats:

        operation,column

    For group operations:

        group_average,group_column,value_column

        group_highest_average,group_column,value_column

    Returns:
        tuple:
            (True, operation, column)
        or:
            (False, None, None)
    """

    # ---------------------------------
    # CHECK RESPONSE TYPE
    # ---------------------------------

    if not isinstance(
        understanding,
        str
    ):

        return (
            False,
            None,
            None
        )


    # ---------------------------------
    # CLEAN RESPONSE
    # ---------------------------------

    understanding = (
        understanding
        .strip()
        .lower()
    )


    # ---------------------------------
    # REMOVE MARKDOWN
    # ---------------------------------

    understanding = (
        understanding
        .replace(
            "```",
            ""
        )
        .replace(
            "`",
            ""
        )
        .strip()
    )


    # ---------------------------------
    # REMOVE COMMON PREFIXES
    # ---------------------------------

    prefixes = [

        "understanding:",

        "answer:",

        "classification:",

        "result:",

        "response:"

    ]


    for prefix in prefixes:

        if understanding.startswith(
            prefix
        ):

            understanding = (
                understanding[
                    len(prefix):
                ]
                .strip()
            )


    # ---------------------------------
    # REMOVE COMMON SENTENCE PREFIXES
    # ---------------------------------

    if ":" in understanding:

        first_part, remaining = (
            understanding.split(
                ":",
                1
            )
        )


        if first_part.strip() in [

            "operation",

            "classification",

            "result",

            "response"

        ]:

            understanding = (
                remaining.strip()
            )


    # ---------------------------------
    # ALLOWED OPERATIONS
    # ---------------------------------

    allowed_operations = [

        "average",

        "median",

        "minimum",

        "maximum",

        "sum",

        "most_common",

        "unique_count",

        "row_count",

        "column_count",

        "missing_values",

        "missing_by_column",

        "duplicate_count",

        "highest_value",

        "lowest_value",

        "group_average",

        "group_highest_average",

        "unsupported",

        "dataset_summary"

    ]


    # ---------------------------------
    # SPLIT RESPONSE
    # ---------------------------------

    parts = [

        part.strip()

        for part in
        understanding.split(",")

    ]


    # ---------------------------------
    # REMOVE EMPTY PARTS
    # ---------------------------------

    parts = [

        part

        for part in parts

        if part

    ]


    # ---------------------------------
    # CHECK EMPTY RESPONSE
    # ---------------------------------

    if not parts:

        return (

            False,

            None,

            None

        )


    # ---------------------------------
    # HANDLE HEADER RESPONSE
    # ---------------------------------

    # Example:
    #
    # operation,row_count
    #
    # Convert to:
    #
    # row_count,None

    if (

        len(parts) == 2

        and parts[0] == "operation"

    ):

        parts = [

            parts[1],

            "none"

        ]


    # ---------------------------------
    # HANDLE GROUP OPERATIONS
    # ---------------------------------

    if (

        len(parts) == 3

        and parts[0] in [

            "group_average",

            "group_highest_average"

        ]

    ):

        operation = parts[0]

        group_column = parts[1]

        value_column = parts[2]


        # ---------------------------------
        # CHECK EMPTY COLUMNS
        # ---------------------------------

        if (

            not group_column

            or not value_column

        ):

            return (

                False,

                None,

                None

            )


        return (

            True,

            operation,

            f"{group_column},{value_column}"

        )


    # ---------------------------------
    # NORMAL OPERATIONS
    # ---------------------------------

    if len(parts) != 2:

        return (

            False,

            None,

            None

        )


    operation = parts[0]

    column = parts[1]


    # ---------------------------------
    # CHECK OPERATION
    # ---------------------------------

    if operation not in allowed_operations:

        return (

            False,

            None,

            None

        )


    # ---------------------------------
    # OPERATIONS WITHOUT COLUMNS
    # ---------------------------------

    no_column_operations = [

        "row_count",

        "column_count",

        "missing_values",

        "duplicate_count"

    ]


    if operation in no_column_operations:

        column = "none"


    # ---------------------------------
    # CHECK COLUMN
    # ---------------------------------

    if not column:

        return (

            False,

            None,

            None

        )


    # ---------------------------------
    # RETURN VALID RESULT
    # ---------------------------------

    return (

        True,

        operation,

        column

    )

# ==========================================================
# UNDERSTAND USER QUESTION
# ==========================================================

def understand_question(
    question,
    dataset_context
):
    """
    Use Ollama to identify what the user wants.

    Ollama receives information about the actual dataset
    so it can better map natural-language questions
    to dataset columns and supported operations.

    Returns:
        str: operation,column
    """

    prompt = f"""
You are the question-understanding component
of an AI Data Analyst application.

Your job is NOT to answer the user's question.

Your job is ONLY to classify the user's question
into one supported operation and identify the
relevant dataset column or columns.

SUPPORTED OPERATIONS:

average
median
minimum
maximum
sum
most_common
unique_count
row_count
column_count
missing_values
missing_by_column
duplicate_count
highest_value
lowest_value
group_average
group_highest_average
unsupported
dataset_summary


DATASET CONTEXT:

{dataset_context}


CLASSIFICATION RULES:

1. ROW COUNT

If the user asks how many records, rows,
employees, people, entries, observations,
or items are in the dataset, use:

row_count,None


Examples:

How many rows are there?
row_count,None

How many employees are there?
row_count,None

How many records are in this dataset?
row_count,None


2. COLUMN COUNT

If the user asks how many columns or fields
the dataset contains, use:

column_count,None


3. AVERAGE

Use average when the user asks for the average
of one numerical column.

Example:

What is the average salary?
average,salary


4. MEDIAN

Use median when the user asks for the median
of one numerical column.

Example:

What is the median age?
median,age


5. MINIMUM

Use minimum when the user asks for the smallest
or minimum value of a numerical column.

Example:

What is the minimum salary?
minimum,salary


6. MAXIMUM

Use maximum when the user asks for the largest
or maximum value of a numerical column.

Example:

What is the maximum salary?
maximum,salary


7. SUM

Use sum when the user asks for the total of
a numerical column.

Example:

What is the total salary?
sum,salary


8. MOST COMMON

Use most_common when the user asks which
categorical value appears most often.

Example:

Which department appears most often?
most_common,department


9. UNIQUE COUNT

Use unique_count when the user asks how many
different or unique values exist in a column.

Example:

How many unique departments are there?
unique_count,department


10. TOTAL MISSING VALUES

Use missing_values when the user asks about
the total number of missing values in the
entire dataset.

Example:

How many missing values are there?
missing_values,None


11. COLUMN MISSING VALUES

Use missing_by_column when the user asks how
many missing values exist in a specific column.

Example:

How many missing values are in Salary?
missing_by_column,salary


12. DUPLICATES

Use duplicate_count when the user asks how many
duplicate rows exist.

Example:

How many duplicate rows are there?
duplicate_count,None


13. HIGHEST VALUE

Use highest_value when the user asks who or what
has the highest value in a numerical column.

Example:

Who has the highest salary?
highest_value,salary

Which employee earns the most?
highest_value,salary


14. LOWEST VALUE

Use lowest_value when the user asks who or what
has the lowest value in a numerical column.

Example:

Who has the lowest salary?
lowest_value,salary

Which employee earns the least?
lowest_value,salary


15. GROUP AVERAGE

Use group_average when the user asks for the
average of a numerical column for every group
in a categorical column.

Return:

group_average,group_column,value_column

Example:

What is the average salary for each department?
group_average,department,salary


16. GROUP HIGHEST AVERAGE

Use group_highest_average when the user asks
which group has the highest average value of
a numerical column.

Return:

group_highest_average,group_column,value_column

Example:

Which department has the highest average salary?
group_highest_average,department,salary

For group_highest_average, identify TWO columns:

  1. The categorical column used to create groups.
  2. The numerical column whose averages are compared.

Example:
Which department pays the most on average?
group_highest_average,department,salary

For group_highest_average, return:

  group_highest_average,group_column,value_column

Example:
What department has the highest average employee salary?
group_highest_average,department,salary


- If the user's question is unrelated to the dataset,
  return:
  unsupported,None

- Questions about weather, news, sports, general knowledge,
  jokes, entertainment, or other topics unrelated to
  the dataset must be classified as unsupported.

- Do not force an unrelated question into a dataset operation.

- Use dataset_summary when the user asks for a general overview,
  summary, or interesting information about the dataset without
  asking for one specific calculation.

- For dataset_summary, return:
  dataset_summary,None

Examples:

What is the weather today?
unsupported,None

Who is the president of the United States?
unsupported,None

Tell me a joke.
unsupported,None

What is the average salary?
average,salary

How many employees are there?
row_count,None

- Use dataset_summary when the user asks for
  a general overview, summary, or interesting
  information about the uploaded dataset.

- Use dataset_summary when the user asks questions
  such as:
  "What can you tell me about this dataset?"
  "Give me an overview of the data."
  "Tell me something interesting about the data."
  "What do you notice about this dataset?"

- For dataset_summary, return:

  dataset_summary,None



IMPORTANT RULES:

- Use ONLY the operations listed above.
- Use ONLY column names that actually exist
  in the dataset context.
- Match column names case-insensitively.
- Do not invent column names.
- Do not answer the user's question.
- Do not explain your decision.
- Do not use markdown.
- Do not add extra text.
- Return ONLY the classification.

For normal operations, return:

operation,column

For group_average, return:

group_average,group_column,value_column

For group_highest_average, return:

group_highest_average,group_column,value_column


USER QUESTION:

{question}

RETURN ONLY THE CLASSIFICATION.
"""

    try:

        response = ollama.chat(

            model="llama3.2:3b",

            messages=[

                {
                    "role": "user",

                    "content": prompt

                }

            ]

        )

        return (
            response["message"]["content"]
            .strip()
        )

    except Exception:

        print("\nOllama Error:")
        traceback.print_exc()

        return "unsupported,None"


# ==========================================================
# IS QUESTION RELEVANT
# ==========================================================


def is_question_relevant(
    question,
    dataset_context
):
    """
    Check whether the user's question is related
    to the uploaded dataset.

    Returns:
        True  -> question is related to dataset
        False -> question is unrelated
    """

    prompt = f"""
You are helping an AI Data Analyst.

Your job is to determine whether the user's question
is related to the uploaded dataset.

Dataset context:

{dataset_context}

User question:

{question}

A question is RELEVANT if it asks about:

- The number of rows
- The number of columns
- Values in dataset columns
- Averages
- Medians
- Minimum or maximum values
- Sums or totals
- Unique values
- Most common values
- Missing values
- Duplicate rows
- Comparisons between dataset values
- Grouped analysis
- Relationships between columns
- Any factual information that can be calculated
  from the uploaded dataset

A question is NOT RELEVANT if it asks about:

- Weather
- News
- Politics
- General knowledge
- Jokes
- Personal advice
- Unrelated calculations
- General internet information
- Topics that cannot be answered using the dataset

Examples:

Question:
How many employees are there?

RELEVANT

Question:
What is the average salary?

RELEVANT

Question:
Which department has the highest average salary?

RELEVANT

Question:
What is the weather today?

NOT_RELEVANT

Question:
Tell me a joke.

NOT_RELEVANT

Question:
Who is the president?

NOT_RELEVANT

Return ONLY one of these two values:

RELEVANT

NOT_RELEVANT

Do not add explanations.
Do not add punctuation.
"""


    try:

        response = ollama.chat(

            model="llama3.2:3b",

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

    except Exception:

        print("\nOllama Error:")
        traceback.print_exc()

        return False


    result = (
        response[
            "message"
        ][
            "content"
        ]
        .strip()
        .upper()
    )


    print(
        "\nQuestion Relevance Check:"
    )

    print(
        result
    )


    if result == "RELEVANT":

        return True


    if result == "NOT_RELEVANT":

        return False


    # ---------------------------------
    # FAIL SAFE
    # ---------------------------------

    return False


# ==========================================================
# UNDERSTAND QUESTION WITH RETRY
# ==========================================================

def understand_question_with_retry(
    question,
    dataset_context,
    max_attempts=3
):
    """
    Ask Ollama to understand a question.

    If the first response is invalid,
    retry up to max_attempts times.
    """

    for attempt in range(
        max_attempts
    ):

        print(
            f"\nOllama Attempt "
            f"{attempt + 1}/{max_attempts}"
        )

        print(
            "Question being classified:"
        )

        print(
            question
        )


        # ---------------------------------
        # ASK OLLAMA
        # ---------------------------------

        understanding = (
            understand_question(

                question,

                dataset_context

            )
        )


        print(
            "Raw Ollama Response:"
        )

        print(
            understanding
        )


        # ---------------------------------
        # VALIDATE RESPONSE
        # ---------------------------------

        is_valid, operation, column = (

            validate_understanding(

                understanding

            )

        )


        if is_valid:

            print(
                "Validated Operation:",
                operation
            )

            print(
                "Validated Column:",
                column
            )


            return (

                True,

                operation,

                column

            )


    # ---------------------------------
    # FINAL FAILURE
    # ---------------------------------

    print(
        "\nOllama failed to provide "
        "a valid understanding."
    )


    return (

        False,

        None,

        None

    )


# ==========================================================
# FIND MATCHING COLUMN
# ==========================================================


def find_matching_column(
    df,
    requested_column
):
    """
    Find the actual dataset column that best
    matches the column identified by Ollama.
    """

    # ---------------------------------
    # CLEAN REQUESTED COLUMN
    # ---------------------------------

    requested_column = (
        requested_column
        .strip()
        .lower()
    )


    # ---------------------------------
    # CHECK FOR EMPTY COLUMN
    # ---------------------------------

    if not requested_column:

        return None


    # ---------------------------------
    # CHECK FOR NONE
    # ---------------------------------

    if requested_column == "none":

        return None


    # ---------------------------------
    # EXACT CASE-INSENSITIVE MATCH
    # ---------------------------------

    for column in df.columns:

        if column.lower() == requested_column:

            return column


    # ---------------------------------
    # NORMALIZE COLUMN NAMES
    # ---------------------------------

    normalized_requested = (
        requested_column
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )


    # ---------------------------------
    # CHECK NORMALIZED MATCH
    # ---------------------------------

    for column in df.columns:

        normalized_column = (
            column.lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )


        if (
            normalized_column
            == normalized_requested
        ):

            return column


    # ---------------------------------
    # CHECK WHETHER REQUESTED WORD
    # APPEARS INSIDE COLUMN NAME
    # ---------------------------------

    for column in df.columns:

        normalized_column = (
            column.lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )


        if (
            normalized_requested
            in normalized_column
        ):

            return column


    # ---------------------------------
    # NO MATCH FOUND
    # ---------------------------------

    return None



# ==========================================================
# ANSWER FROM UNDERSTANDING
# ==========================================================

def answer_from_understanding(
    df,
    operation,
    column
):
    """
    Calculate the factual answer using Python.
    """

    operation = (

        operation

        .strip()

        .lower()

    )

    column = (

        column

        .strip()

    )
    

    # ======================================================
    # DATASET SUMMARY
    # ======================================================

    if operation == "dataset_summary":

        return generate_dataset_summary(
            df
        )


    # ======================================================
    # GROUP OPERATIONS
    # ======================================================

    if operation in [

        "group_average",

        "group_highest_average"

    ]:

        try:

            group_column, value_column = (

                column.split(

                    ",",

                    1

                )

            )

        except ValueError:

            return (

                "I could not identify the "
                "required columns."

            )


        group_column = (

            group_column.strip()

        )

        value_column = (

            value_column.strip()

        )


        # ---------------------------------
        # FIND ACTUAL COLUMNS
        # ---------------------------------

        actual_group_column = None

        actual_value_column = None


        for col in df.columns:

            if (

                col.lower()

                ==

                group_column.lower()

            ):

                actual_group_column = col


            if (

                col.lower()

                ==

                value_column.lower()

            ):

                actual_value_column = col


        if actual_group_column is None:

            return (

                f"I could not identify the "
                f"grouping column "
                f"'{group_column}'."

            )


        if actual_value_column is None:

            return (

                f"I could not identify the "
                f"value column "
                f"'{value_column}'."

            )


        # ---------------------------------
        # CHECK NUMERICAL COLUMN
        # ---------------------------------

        if not pd.api.types.is_numeric_dtype(

            df[actual_value_column]

        ):

            return (

                f"The column "
                f"'{actual_value_column}' "
                f"is not a numerical column."

            )


        # ---------------------------------
        # CALCULATE GROUP AVERAGES
        # ---------------------------------

        grouped_averages = (

            df.groupby(

                actual_group_column

            )[actual_value_column]

            .mean()

        )


        if grouped_averages.empty:

            return (

                "No grouped averages "
                "could be calculated."

            )


        # ---------------------------------
        # GROUP AVERAGE
        # ---------------------------------

        if operation == "group_average":

            results = []


            for group, average in (

                grouped_averages.items()

            ):

                results.append(

                    f"{group}: "
                    f"{average:,.2f}"

                )


            return (

                f"Average "
                f"{actual_value_column} "
                f"by "
                f"{actual_group_column}: "

                +

                "; ".join(

                    results

                )

                +

                "."

            )


        # ---------------------------------
        # GROUP HIGHEST AVERAGE
        # ---------------------------------

        if operation == "group_highest_average":

            highest_group = (

                grouped_averages.idxmax()

            )

            highest_average = (

                grouped_averages.max()

            )


            return (

                f"The "
                f"{actual_group_column} "
                f"with the highest average "
                f"{actual_value_column} "
                f"is "
                f"{highest_group}, "
                f"with an average value "
                f"of "
                f"{highest_average:,.2f}."

            )


    # ======================================================
    # ROW COUNT
    # ======================================================

    if operation == "row_count":

        return (

            f"The dataset contains "

            f"{len(df)} "

            f"rows."

        )
    

    # ======================================================
    # COLUMN COUNT
    # ======================================================

    if operation == "column_count":

        return (

            f"The dataset contains "

            f"{len(df.columns)} "

            f"columns."

        )


    # ======================================================
    # TOTAL MISSING VALUES
    # ======================================================

    if operation == "missing_values":

        total = int(

            df.isnull()

            .sum()

            .sum()

        )


        return (

            f"The dataset contains "

            f"{total} "

            f"missing values."

        )


    # ======================================================
    # DUPLICATE ROW COUNT
    # ======================================================

    if operation == "duplicate_count":

        duplicates = int(

            df.duplicated()

            .sum()

        )


        return (

            f"The dataset contains "

            f"{duplicates} "

            f"duplicate rows."

        )


    # ======================================================
    # FIND ACTUAL COLUMN
    # ======================================================

    actual_column = None

    if column.lower() != "none":

        actual_column = find_matching_column(
            df,
            column
        )


        if actual_column is None:

            return (
                f"I could not identify "
                f"the requested column '{column}'."
            )


    # ======================================================
    # MISSING VALUES BY COLUMN
    # ======================================================

    if operation == "missing_by_column":

        missing_count = int(

            df[actual_column]

            .isnull()

            .sum()

        )


        return (

            f"The column "
            f"'{actual_column}' "
            f"contains "
            f"{missing_count} "
            f"missing values."

        )


    # ======================================================
    # NUMERICAL OPERATIONS
    # ======================================================

    if operation in [

        "average",

        "median",

        "minimum",

        "maximum",

        "sum"

    ]:

        if not pd.api.types.is_numeric_dtype(

            df[actual_column]

        ):

            return (

                f"The column "
                f"'{actual_column}' "
                f"is not a numerical column."

            )


        if operation == "average":

            value = (

                df[actual_column]

                .mean()

            )


            return (

                f"The average value of "
                f"{actual_column} "
                f"is "
                f"{value:,.2f}."

            )


        if operation == "median":

            value = (

                df[actual_column]

                .median()

            )


            return (

                f"The median value of "
                f"{actual_column} "
                f"is "
                f"{value:.2f}."

            )


        if operation == "minimum":

            value = (

                df[actual_column]

                .min()

            )


            return (

                f"The minimum value of "
                f"{actual_column} "
                f"is "
                f"{value:,.2f}."

            )


        if operation == "maximum":

            value = (

                df[actual_column]

                .max()

            )


            return (

                f"The maximum value of "
                f"{actual_column} "
                f"is "
                f"{value:,.2f}."

            )


        if operation == "sum":

            value = (

                df[actual_column]

                .sum()

            )


            return (

                f"The total sum of "
                f"{actual_column} "
                f"is "
                f"{value:,.2f}."

            )


    # ======================================================
    # HIGHEST VALUE
    # ======================================================

    if operation == "highest_value":

        if not pd.api.types.is_numeric_dtype(

            df[actual_column]

        ):

            return (

                f"The column "
                f"'{actual_column}' "
                f"is not a numerical column."

            )


        max_index = (

            df[actual_column]

            .idxmax()

        )


        max_value = (

            df.loc[

                max_index,

                actual_column

            ]

        )


        name_column = None


        for col in df.columns:

            if col.lower() in [

                "name",

                "employee",

                "employee_name"

            ]:

                name_column = col

                break


        if name_column:

            person = (

                df.loc[

                    max_index,

                    name_column

                ]

            )


            return (

                f"{person} has the highest "
                f"{actual_column} value, "
                f"which is "
                f"{max_value}."

            )


        return (

            f"The highest value in "
            f"{actual_column} "
            f"is "
            f"{max_value}."

        )


    # ======================================================
    # LOWEST VALUE
    # ======================================================

    if operation == "lowest_value":

        if not pd.api.types.is_numeric_dtype(

            df[actual_column]

        ):

            return (

                f"The column "
                f"'{actual_column}' "
                f"is not a numerical column."

            )


        min_index = (

            df[actual_column]

            .idxmin()

        )


        min_value = (

            df.loc[

                min_index,

                actual_column

            ]

        )


        name_column = None


        for col in df.columns:

            if col.lower() in [

                "name",

                "employee",

                "employee_name"

            ]:

                name_column = col

                break


        if name_column:

            person = (

                df.loc[

                    min_index,

                    name_column

                ]

            )


            return (

                f"{person} has the lowest "
                f"{actual_column} value, "
                f"which is "
                f"{min_value}."

            )


        return (

            f"The lowest value in "
            f"{actual_column} "
            f"is "
            f"{min_value}."

        )


    # ======================================================
    # UNIQUE VALUE COUNT
    # ======================================================

    if operation == "unique_count":

        unique_count = (

            df[actual_column]

            .nunique(

                dropna=True

            )

        )


        return (

            f"The column "
            f"'{actual_column}' "
            f"contains "
            f"{unique_count} "
            f"unique values."

        )


    # ======================================================
    # MOST COMMON VALUE
    # ======================================================

    if operation == "most_common":

        value_counts = (

            df[actual_column]

            .value_counts()

        )


        if value_counts.empty:

            return (

                f"The column "
                f"'{actual_column}' "
                f"does not contain "
                f"any values."

            )


        value = (

            value_counts

            .idxmax()

        )


        frequency = (

            value_counts

            .max()

        )


        return (

            f"The most common value "
            f"in "
            f"{actual_column} "
            f"is "
            f"{value}, "
            f"appearing "
            f"{frequency} "
            f"times."

        )


    # ======================================================
    # UNSUPPORTED QUESTION
    # ======================================================
    
    if operation == "unsupported":
        return (
            "I'm sorry, but I can only answer questions "
            "related to the uploaded dataset."
        )
   
    # ======================================================
    # FALLBACK
    # ======================================================

    return (

        "I couldn't answer that question yet."

    )

    # ======================================================
    # DATASET SUMMARY
    # ======================================================

    if operation == "dataset_summary":

        return (

            "I can provide a summary of the "
            "dataset based on its rows, columns, "
            "data quality, and available analysis."

        )


# ==========================================================
# SIMPLE QUESTION CHECK
# ==========================================================

def is_simple_question(
    operation
):

    simple_operations = [

        "row_count",

        "column_count",

        "average",

        "median",

        "minimum",

        "maximum",

        "sum",

        "unique_count",

        "missing_values",

        "missing_by_column",

        "duplicate_count",

        "most_common",

        "highest_value",

        "lowest_value",

        "group_average",

        "group_highest_average",

        "dataset_summary",

        "unsupported"

    ]


    return (

        operation

        in

        simple_operations

    )



# ==========================================================
# LOCAL TESTING
# ==========================================================

if __name__ == "__main__":

    df = pd.read_csv(

        "uploads/employees.csv"

    )


    dataset_context = (

        generate_dataset_context(

            df

        )

    )


    test_questions = [

        "How many rows are there?",

        "How many employees are there?",

        "How many columns are there?",

        "What is the average salary?",

        "What is the median salary?",

        "What is the minimum age?",

        "What is the maximum salary?",

        "What is the total salary?",

        "Which department appears most often?",

        "How many unique departments are there?",

        "How many missing values are there?",

        "How many missing values are in Salary?",

        "How many duplicate rows are there?",

        "What is the average salary for each department?",

        "Which department has the highest average salary?"

    ]


    for question in test_questions:

        print(

            "\n"

            + "=" * 60

        )


        print(

            "Question:"

        )


        print(

            question

        )


        is_valid, operation, column = (

            understand_question_with_retry(

                question,

                dataset_context

            )

        )


        if is_valid:

            answer = (

                answer_from_understanding(

                    df,

                    operation,

                    column

                )

            )


            print(

                "\nAnswer:"

            )


            print(

                answer

            )


        else:

            print(

                "\nCould not understand question."

            )