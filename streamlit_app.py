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


def inject_datamind_styles():
    """Apply the visual language from the redesigned Flask interface."""
    st.markdown(
        """
        <style>
        :root {
          --dm-forest: #064e3b;
          --dm-forest-mid: #065f46;
          --dm-teal: #0f766e;
          --dm-mint: #b9dfd1;
          --dm-mint-soft: #dcefe8;
          --dm-ink: #111827;
          --dm-slate: #475569;
          --dm-muted: #64748b;
          --dm-canvas: #f4f7f6;
          --dm-line: #dce5e1;
        }

        [data-testid="stAppViewContainer"] { background: var(--dm-canvas); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }
        [data-testid="stDecoration"] { display: none; }
        .block-container {
          max-width: 1200px;
          padding: 1.5rem 2rem 4rem;
        }
        h1, h2, h3, h4, p, label, [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
          color: var(--dm-ink) !important;
        }
        h1, h2, h3, h4 { font-family: "Trebuchet MS", "Arial", sans-serif; }
        h1 { letter-spacing: -0.04em; }
        h2 { font-size: 1.35rem; }
        h3 { font-size: 1.05rem; }

        .dm-header {
          display: flex; align-items: center; justify-content: space-between;
          gap: 1.5rem; margin: -0.5rem 0 2.25rem; padding: 0.9rem 1.2rem;
          color: var(--dm-mint-soft); background: var(--dm-forest);
          border-radius: 12px; box-shadow: 0 12px 30px rgba(6,78,59,.12);
        }
        .dm-brand { display: flex; align-items: center; gap: .75rem; }
        .dm-mark {
          display: grid; place-items: center; width: 2.2rem; height: 2.2rem;
          border: 1px solid rgba(236,253,245,.3); border-radius: 9px;
          color: var(--dm-mint-soft); background: rgba(236,253,245,.12);
          font-size: 1.2rem; font-weight: 800;
        }
        .dm-name { font-size: 1.08rem; font-weight: 800; line-height: 1.1; }
        .dm-tagline { margin-top: .18rem; color: rgba(236,253,245,.68); font-size: .67rem; }
        .dm-nav { display: flex; gap: .35rem; color: rgba(236,253,245,.75); font-size: .78rem; }
        .dm-nav span { padding: .45rem .6rem; border-radius: 6px; }
        .dm-nav .active { color: var(--dm-forest); background: var(--dm-mint-soft); }

        .dm-hero { margin-bottom: 1.4rem; }
        .dm-eyebrow {
          margin-bottom: .35rem; color: var(--dm-teal); font-size: .7rem;
          font-weight: 800; letter-spacing: .14em; text-transform: uppercase;
        }
        .dm-hero-copy { max-width: 680px; color: var(--dm-slate); font-size: .98rem; }
        .dm-hero-copy strong { color: var(--dm-teal); }
        .dm-loaded {
          margin: 1.1rem 0 1.25rem; padding: .9rem 1rem; border-radius: 10px;
          color: var(--dm-forest); background: var(--dm-mint);
          border: 1px solid rgba(6,78,59,.12); font-size: .9rem; font-weight: 700;
        }
        .dm-empty-state {
          margin: 1.25rem 0; padding: 1rem 1.15rem; border-radius: 10px;
          color: var(--dm-forest); background: white;
          border: 1px solid var(--dm-line); font-size: .95rem;
        }
        .dm-section {
          margin: 1rem 0; padding: 1.2rem 1.35rem; border: 1px solid rgba(6,78,59,.09);
          border-radius: 12px; background: rgba(255,255,255,.86);
          box-shadow: 0 7px 24px rgba(6,78,59,.045);
        }

        [data-testid="stMetric"] {
          padding: 1rem 1.1rem; border: 1px solid rgba(6,78,59,.09);
          border-radius: 10px; background: rgba(255,255,255,.9);
          box-shadow: 0 7px 24px rgba(6,78,59,.045);
        }
        [data-testid="stMetricLabel"] { color: var(--dm-muted) !important; font-size: .78rem; }
        [data-testid="stMetricValue"] { color: var(--dm-forest) !important; font-size: 1.8rem; }

        [data-testid="stFileUploader"] section {
          min-height: 8rem; padding: 1.25rem; border: 1.5px dashed rgba(15,118,110,.48);
          border-radius: 10px; background: #d6ebe3;
        }
        [data-testid="stFileUploader"] section:hover {
          background: #d6ebe3 !important;
        }
        [data-testid="stFileUploader"] small,
        [data-testid="stFileUploader"] p { color: var(--dm-slate) !important; }
        [data-testid="stFileUploader"] button {
          color: white !important; border-color: var(--dm-forest); background: var(--dm-forest);
          font-weight: 700;
        }
        [data-testid="stFileUploader"] button * { color: white !important; }
        [data-testid="stFileUploader"] button:hover,
        [data-testid="stFileUploader"] button:focus,
        [data-testid="stFileUploader"] button:active {
          color: white !important; border-color: var(--dm-forest) !important;
          background: var(--dm-forest) !important; box-shadow: none !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
          gap: .45rem; padding: .35rem; border: 1px solid var(--dm-line);
          border-radius: 10px; background: rgba(255,255,255,.68);
        }
        [data-testid="stTabs"] [data-baseweb="tab"] {
          min-height: 2.7rem; padding: .7rem 1rem; border-radius: 7px;
          color: var(--dm-slate); font-size: .92rem; font-weight: 600;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
          color: white !important; background: var(--dm-forest); font-weight: 800;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] * { color: white !important; }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }
        .stButton > button {
          min-height: 2.55rem; border: 1px solid var(--dm-forest);
          border-radius: 8px; color: white !important; background: var(--dm-forest);
          font-weight: 700;
        }
        .stButton > button * { color: white !important; }
        .stButton > button:hover { color: white !important; border-color: var(--dm-forest-mid); background: var(--dm-forest-mid); }
        [data-testid="stAlert"] { border-radius: 10px; color: var(--dm-forest) !important; background: #e0efe9; }
        [data-testid="stAlert"] p { color: var(--dm-forest) !important; }
        [data-testid="stTextInput"] input {
          color: var(--dm-ink) !important; background: white !important;
          border-color: var(--dm-line) !important;
        }
        [data-testid="stTextInput"] input:focus { border-color: var(--dm-teal) !important; }
        [data-testid="stDataFrame"] { border: 1px solid var(--dm-line); border-radius: 9px; overflow: hidden; }
        .dm-table-wrap { overflow-x: auto; border: 1px solid #c9ddd6; border-radius: 10px; }
        .dm-table {
          width: 100%; border-collapse: separate; border-spacing: 0;
          color: var(--dm-ink); background: white; font-size: .9rem;
        }
        .dm-table th {
          padding: .72rem .8rem; color: white; background: var(--dm-forest);
          border-right: 1px solid rgba(255,255,255,.18); font-weight: 700;
          text-align: left; white-space: nowrap;
        }
        .dm-table td {
          padding: .65rem .8rem; color: var(--dm-ink); background: white;
          border-top: 1px solid #dce5e1; border-right: 1px solid #dce5e1;
        }
        .dm-table tbody tr:nth-child(even) td { background: #f1f8f5; }
        .dm-table th:last-child, .dm-table td:last-child { border-right: 0; }
        [data-testid="stImage"] img { border-radius: 8px; border: 1px solid var(--dm-line); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_table(frame, *, hide_index=True):
    """Render a readable light table with a DataMind-green header."""
    table = frame.to_html(
        index=not hide_index,
        classes="dm-table",
        border=0,
        escape=True,
    )
    st.markdown(f'<div class="dm-table-wrap">{table}</div>', unsafe_allow_html=True)


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
    inject_datamind_styles()
    st.markdown(
        """
        <header class="dm-header">
          <div class="dm-brand">
          <div class="dm-mark">DM</div>
            <div><div class="dm-name">DataMind</div>
            <div class="dm-tagline">Your AI Data Analyst</div></div>
          </div>
        </header>
        <section class="dm-hero">
          <div class="dm-eyebrow">AI data analyst</div>
          <h1>Understand your data. <span style="color:#0f766e">Instantly.</span></h1>
          <p class="dm-hero-copy">Upload a CSV dataset and discover insights, patterns, quality issues, and relationships <strong>without writing code.</strong></p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload your CSV dataset",
        type=["csv"],
        help="DataMind currently accepts CSV files.",
    )

    if uploaded_file is None:
        st.markdown(
            '<p class="dm-empty-state">Upload a CSV file to begin your analysis.</p>',
            unsafe_allow_html=True,
        )
        return

    try:
        df = read_dataset(uploaded_file.getvalue())
    except Exception as error:
        st.error(f"The CSV could not be read: {error}")
        return

    if df.empty or len(df.columns) == 0:
        st.error("The uploaded CSV does not contain any data.")
        return

    st.markdown(
        f'<div class="dm-loaded">✓ Loaded {uploaded_file.name}</div>',
        unsafe_allow_html=True,
    )

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
        render_table(df.head(10))
        st.subheader("Column information")
        overview = get_dataset_overview(df)
        column_info = pd.DataFrame(
            {
                "Column": list(overview["data_types"].keys()),
                "Data type": list(overview["data_types"].values()),
            }
        )
        render_table(column_info, hide_index=True)

    with quality_tab:
        st.subheader(f"Dataset health: {quality_report['health']}")
        for observation in quality_report["observations"]:
            st.write(f"• {observation}")
        st.subheader("Missing values by column")
        missing = pd.Series(quality_report["missing_values"], name="Missing values")
        missing_table = missing.rename_axis("Column").reset_index()
        render_table(missing_table)
        st.subheader("Potential outliers")
        if outliers:
            render_table(
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
        st.caption(
            "Ask about averages, missing values, relationships, or category counts. "
            "DataMind calculates the answer from your uploaded data."
        )
        question = st.text_input(
            "Your question",
            placeholder="e.g., What is the average salary?",
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
