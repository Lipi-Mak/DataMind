"""Streamlit entry point for DataMind.

This file is intentionally separate from the existing Flask app so the
original application remains available while the Streamlit version is built.
All factual calculations continue to come from the existing Python utilities.
"""

import io
import os

import pandas as pd
import streamlit as st

from utils.analyzer import get_dataset_overview
from utils.insight_generator import generate_factual_insights
from utils.key_findings import generate_key_findings, get_top_findings
from utils.outlier_detector import detect_outliers
from utils.quality_checker import generate_quality_report
from utils.question_answerer import (
    answer_from_understanding,
    generate_dataset_context,
)
from utils.relationship_detector import (
    detect_relationships,
    generate_relationship_findings,
)
from utils.visualizer import (
    create_all_bar_charts,
    create_all_boxplots,
    create_all_histograms,
    create_correlation_heatmap,
)
from utils.gemini_provider import (
    classify_question,
    explain_verified_insights,
    explain_verified_results,
    gemini_available,
)


st.set_page_config(
    page_title="DataMind",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def read_dataset(file_bytes):
    """Read an uploaded CSV into a DataFrame."""
    return pd.read_csv(io.BytesIO(file_bytes))


def render_metric_row(df, quality_report):
    """Render the high-level dataset metrics."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{len(df):,}")
    col2.metric("Columns", f"{len(df.columns):,}")
    col3.metric("Missing values", f"{quality_report['total_missing']:,}")
    col4.metric("Duplicate rows", f"{quality_report['duplicate_rows']:,}")


def render_visualizations(df):
    """Create and display the existing Matplotlib visualizations."""
    with st.spinner("Creating visualizations..."):
        histogram_paths = create_all_histograms(df)
        boxplot_paths = create_all_boxplots(df)
        heatmap_path = create_correlation_heatmap(df)
        bar_chart_paths = create_all_bar_charts(df)

    st.subheader("Histograms")
    if histogram_paths:
        columns = st.columns(2)
        for index, path in enumerate(histogram_paths):
            with columns[index % 2]:
                st.image(path, caption=os.path.basename(path))
    else:
        st.info("No suitable numerical columns were found for histograms.")

    st.subheader("Box plots")
    if boxplot_paths:
        columns = st.columns(2)
        for index, path in enumerate(boxplot_paths):
            with columns[index % 2]:
                st.image(path, caption=os.path.basename(path))
    else:
        st.info("No suitable numerical columns were found for box plots.")

    st.subheader("Correlation heatmap")
    if heatmap_path:
        st.image(heatmap_path)
    else:
        st.info("At least two suitable numerical columns are needed.")

    st.subheader("Category charts")
    if bar_chart_paths:
        columns = st.columns(2)
        for index, path in enumerate(bar_chart_paths):
            with columns[index % 2]:
                st.image(path, caption=os.path.basename(path))
    else:
        st.info("No suitable categorical columns were found for bar charts.")


def main():
    st.title("DataMind")
    st.caption("Your AI data analyst — upload a CSV to explore it.")

    uploaded_file = st.file_uploader(
        "Upload a CSV dataset",
        type=["csv"],
        help="DataMind currently accepts CSV files.",
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin your analysis.")
        return

    try:
        df = read_dataset(uploaded_file.getvalue())
    except Exception as error:
        st.error(f"The CSV could not be read: {error}")
        return

    if df.empty or len(df.columns) == 0:
        st.error("The uploaded CSV does not contain any data.")
        return

    st.success(f"Loaded {uploaded_file.name}")

    quality_report = generate_quality_report(df)
    factual_insights, _ = generate_factual_insights(df)
    outliers = detect_outliers(df)
    relationships = detect_relationships(df)
    relationship_findings = generate_relationship_findings(relationships)
    key_findings = generate_key_findings(
        quality_report,
        outliers,
        relationships,
        factual_insights,
    )

    render_metric_row(df, quality_report)

    overview_tab, quality_tab, charts_tab, insights_tab, ask_tab = st.tabs(
        ["Overview", "Data quality", "Visualizations", "Insights", "Ask DataMind"]
    )

    with overview_tab:
        st.subheader("Dataset preview")
        st.dataframe(df.head(10), use_container_width=True)
        st.subheader("Column information")
        overview = get_dataset_overview(df)
        column_info = pd.DataFrame(
            {
                "Column": list(overview["data_types"].keys()),
                "Data type": list(overview["data_types"].values()),
            }
        )
        st.dataframe(column_info, hide_index=True, use_container_width=True)

    with quality_tab:
        st.subheader(f"Dataset health: {quality_report['health']}")
        for observation in quality_report["observations"]:
            st.write(f"• {observation}")
        st.subheader("Missing values by column")
        missing = pd.Series(quality_report["missing_values"], name="Missing values")
        st.dataframe(missing.to_frame(), use_container_width=True)
        st.subheader("Potential outliers")
        if outliers:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Column": item["column"],
                            "Count": item["count"],
                            "Values": item["values"],
                        }
                        for item in outliers
                    ]
                ),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.success("No potential outliers were detected using the IQR method.")

    with charts_tab:
        render_visualizations(df)

    with insights_tab:
        st.subheader("Key findings")
        for finding in get_top_findings(key_findings):
            st.markdown(f"**{finding['title']}** — {finding['description']}")

        st.subheader("Factual insights")
        for insight in factual_insights:
            st.write(f"• {insight}")

        if relationship_findings:
            st.subheader("Relationships")
            for finding in relationship_findings:
                st.write(f"• {finding}")

        st.subheader("Gemini explanation")
        if not gemini_available():
            st.info(
                "Add GEMINI_API_KEY to Streamlit secrets to enable AI explanations."
            )
        elif st.button("Explain these verified findings", key="explain_findings"):
            with st.spinner("Preparing an explanation..."):
                try:
                    explanation = explain_verified_insights(
                        factual_insights,
                        relationship_findings,
                    )
                    st.markdown(explanation)
                except Exception as error:
                    st.error(f"Gemini could not generate an explanation: {error}")

    with ask_tab:
        st.subheader("Ask a question about your dataset")
        question = st.text_input(
            "Try: What is the average salary?",
            key="dataset_question",
        )

        if st.button("Ask DataMind", key="ask_datamind"):
            if not question.strip():
                st.warning("Please enter a question first.")
            elif not gemini_available():
                st.warning(
                    "Ask DataMind needs a GEMINI_API_KEY. The factual analysis "
                    "above still works without it."
                )
            else:
                with st.spinner("Analyzing your question..."):
                    try:
                        operation, column = classify_question(
                            question,
                            generate_dataset_context(df),
                        )
                        factual_answer = answer_from_understanding(
                            df,
                            operation,
                            column,
                        )

                        if operation == "unsupported":
                            st.info(
                                "I can only answer questions related to the "
                                "uploaded dataset."
                            )
                        else:
                            explanation = explain_verified_results(
                                question,
                                factual_answer,
                            )
                            st.markdown(explanation)
                    except Exception as error:
                        st.error(f"DataMind could not answer that question: {error}")


if __name__ == "__main__":
    main()
