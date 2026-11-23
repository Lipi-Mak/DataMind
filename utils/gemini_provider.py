"""Optional Gemini provider for public DataMind deployments.

Python calculates the answer first. Gemini only classifies a user's question
or explains results that have already been calculated by Python.
"""

import os

try:
    import streamlit as st
except ImportError:  # pragma: no cover - used outside Streamlit
    st = None


MODEL_NAME = "gemini-2.5-flash-lite"


def _get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    if st is not None:
        try:
            return st.secrets.get("GEMINI_API_KEY")
        except Exception:
            return None

    return None


def gemini_available():
    """Return whether a Gemini key is configured."""
    return bool(_get_api_key())


def _generate(prompt):
    """Generate text with Gemini, returning a clear error on failure."""
    from google import genai

    client = genai.Client(api_key=_get_api_key())
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text.strip()


def explain_verified_results(question, factual_answer):
    """Explain a Python-calculated answer without doing new calculations."""
    prompt = f"""
You are DataMind, a careful data-analysis assistant.

The user asked:
{question}

Python already calculated this factual answer:
{factual_answer}

Explain the answer clearly in one or two short sentences.
Use only the factual answer provided above.
Do not calculate anything new, change numbers, invent information, or infer
causes. Return only the answer for the user.
"""
    return _generate(prompt)


def explain_verified_insights(factual_insights, relationship_findings):
    """Turn verified Python findings into a concise human summary."""
    facts = "\n".join(f"- {item}" for item in factual_insights)
    relationships = "\n".join(f"- {item}" for item in relationship_findings)
    prompt = f"""
You are DataMind, a careful data-analysis assistant.

Python produced the following verified facts:
{facts}

Verified relationships, if any:
{relationships or "None"}

Write a concise summary with the headings Key observations and Data quality.
Use only the facts supplied above. Do not calculate new statistics, change
numbers, infer causes, or add outside information.
"""
    return _generate(prompt)


def classify_question(question, dataset_context):
    """Map a natural-language question to a safe Python operation."""
    operations = """
row_count, column_count, average, median, minimum, maximum, sum,
unique_count, missing_values, missing_by_column, duplicate_count,
most_common, highest_value, lowest_value, dataset_summary, unsupported
"""
    prompt = f"""
You classify questions for a data-analysis application.

Dataset context:
{dataset_context}

User question:
{question}

Supported operations:
{operations}

Return exactly one line in this format:
operation|column

For row_count, column_count, missing_values, or duplicate_count, use None as
the column. For questions unrelated to this dataset or unsupported questions,
return unsupported|None. Use the exact column name from the dataset.
Do not return any explanation.
"""
    result = _generate(prompt).splitlines()[0].strip()
    parts = [part.strip() for part in result.split("|", 1)]
    if len(parts) != 2:
        return "unsupported", ""
    return parts[0].lower(), parts[1]
