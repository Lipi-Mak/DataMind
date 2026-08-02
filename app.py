from flask import Flask, render_template, request, session, redirect, url_for
import os
import pandas as pd

from utils.file_handler import process_uploaded_file
from utils.analyzer import get_dataset_overview
from utils.quality_checker import generate_quality_report
from utils.visualizer import (
    create_all_histograms,
    create_all_boxplots,
    create_correlation_heatmap,
    create_all_bar_charts
)

from utils.insight_generator import (
    generate_factual_insights,
    generate_ai_insights,
    generate_ai_outlier_explanations,
    generate_ai_key_findings
)

from utils.question_answerer import (
    generate_dataset_context,
    understand_question,
    answer_from_understanding,
    validate_understanding,
    understand_question_with_retry,
    is_simple_question,
    is_question_relevant
)

from utils.insight_generator import explain_answer

from utils.outlier_detector import (
    detect_outliers
)

from utils.key_findings import (
    generate_key_findings,
    get_top_findings
)

from utils.relationship_detector import (
    detect_relationships,
    generate_relationship_findings
)

app = Flask(__name__)


# ==========================================================
# GLOBAL ERROR HANDLER
# ==========================================================

@app.errorhandler(500)
def internal_server_error(error):

    print(
        "\nInternal Server Error:"
    )

    print(
        error
    )

    return render_template(
        "error.html",
        message=(
            "Something went wrong while "
            "processing your request. "
            "Please try again."
        )
    ), 500


app.secret_key = "datamind_secret_key"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        file = request.files["dataset"]

        success, result = process_uploaded_file(
            file,
            app.config["UPLOAD_FOLDER"]
        )

        if success:

            session["dataset_path"] = result["filepath"]
            session["filename"] = file.filename

            return redirect(url_for("overview"))

        return render_template(
            "index.html",
            error=result["error"]
        )

    return render_template("index.html")


@app.route("/overview")
def overview():

    if "dataset_path" not in session:
        return redirect(url_for("home"))

    df = pd.read_csv(session["dataset_path"])

    overview = get_dataset_overview(df)

    return render_template(
        "overview.html",
        overview=overview,
        filename=session["filename"]
    )


@app.route("/quality")
def quality():

    if "dataset_path" not in session:
        return redirect(url_for("home"))

    df = pd.read_csv(session["dataset_path"])
    
    report = generate_quality_report(df)

    return render_template(
        "quality.html",
        report=report,
        filename=session["filename"]
    )

@app.route("/visualizations")
def visualizations():

    if "dataset_path" not in session:
        return redirect(url_for("home"))

    df = pd.read_csv(session["dataset_path"])

    histogram_paths = create_all_histograms(df)

    boxplot_paths = create_all_boxplots(df)

    heatmap_path = create_correlation_heatmap(df)

    bar_chart_paths = create_all_bar_charts(df)

    print("Histogram paths:", histogram_paths)
    print("Box plot paths:", boxplot_paths)
    print("Heatmap path:", heatmap_path)
    print("Bar chart paths:", bar_chart_paths)

    histogram_paths = [
        f"charts/{os.path.basename(path)}"
        for path in histogram_paths
    ]

    boxplot_paths = [
        f"charts/{os.path.basename(path)}"
        for path in boxplot_paths
    ]

    bar_chart_paths = [
        f"charts/{os.path.basename(path)}"
        for path in bar_chart_paths
    ]

    if heatmap_path:
        heatmap_path = f"charts/{os.path.basename(heatmap_path)}"

    return render_template(
        "visualizations.html",
        histogram_paths=histogram_paths,
        boxplot_paths=boxplot_paths,
        heatmap_path=heatmap_path,
        bar_chart_paths=bar_chart_paths,
        filename=session["filename"]
    )


@app.route("/ask", methods=["GET", "POST"])
def ask():

    if "dataset_path" not in session:
        return redirect(url_for("home"))

    answer = None
    question = ""

    if request.method == "POST":

        try:

            # ---------------------------------
            # GET USER QUESTION
            # ---------------------------------

            question = request.form.get(
                "question",
                ""
            ).strip()


            # ---------------------------------
            # GET SUGGESTED QUESTION DATA
            # ---------------------------------

            suggested_operation = request.form.get(
                "suggested_operation",
                ""
            ).strip().lower()


            suggested_column = request.form.get(
                "suggested_column",
                ""
            ).strip()


            # ---------------------------------
            # LOAD DATASET
            # ---------------------------------

            df = pd.read_csv(
                session["dataset_path"]
            )


            # ---------------------------------
            # GENERATE DATASET CONTEXT
            # ---------------------------------

            dataset_context = generate_dataset_context(
                df
            )


            # ---------------------------------
            # CHECK IF SUGGESTED QUESTION
            # ---------------------------------

            if suggested_operation:

                print("\nSuggested Question:")
                print(question)

                print("\nSuggested Operation:")
                print(suggested_operation)

                print("\nSuggested Column:")
                print(suggested_column)


                # ---------------------------------
                # USE PREDEFINED OPERATION
                # ---------------------------------

                operation = suggested_operation
                column = suggested_column


                # ---------------------------------
                # CALCULATE FACTUAL ANSWER
                # ---------------------------------

                factual_answer = answer_from_understanding(
                    df,
                    operation,
                    column
                )


                print("\nFactual Answer:")
                print(factual_answer)


                # ---------------------------------
                # HANDLE RESPONSE
                # ---------------------------------

                if operation == "unsupported":

                    answer = (
                        "I'm sorry, but I can only answer "
                        "questions related to the uploaded dataset."
                    )

                elif is_simple_question(operation):

                    answer = factual_answer

                else:

                    answer = explain_answer(
                        question,
                        factual_answer
                    )


            # ---------------------------------
            # MANUAL USER QUESTION
            # ---------------------------------

            else:

                print("\nManual User Question:")
                print(question)


                # ---------------------------------
                # CHECK QUESTION RELEVANCE
                # ---------------------------------

                is_relevant = is_question_relevant(
                    question,
                    dataset_context
                )


                print("\nQuestion Relevant:")
                print(is_relevant)


                # ---------------------------------
                # HANDLE UNRELATED QUESTION
                # ---------------------------------

                if not is_relevant:

                    answer = (
                        "I'm sorry, but I can only "
                        "answer questions related to "
                        "your uploaded dataset. "
                        "Please ask me something about "
                        "the data."
                    )


                else:

                    # ---------------------------------
                    # UNDERSTAND QUESTION
                    # ---------------------------------

                    is_valid, operation, column = (
                        understand_question_with_retry(
                            question,
                            dataset_context
                        )
                    )


                    print("\nValidated Operation:")
                    print(operation)

                    print("\nValidated Column:")
                    print(column)


                    # ---------------------------------
                    # HANDLE INVALID QUESTION
                    # ---------------------------------

                    if not is_valid:

                        answer = (
                            "I'm sorry, but I couldn't "
                            "understand that question. "
                            "Please try asking something "
                            "about the data in your dataset."
                        )

                    else:

                        # ---------------------------------
                        # GET FACTUAL ANSWER
                        # ---------------------------------

                        factual_answer = (
                            answer_from_understanding(
                                df,
                                operation,
                                column
                            )
                        )


                        print("\nFactual Answer:")
                        print(factual_answer)


                        # ---------------------------------
                        # HANDLE RESPONSE
                        # ---------------------------------

                        if operation == "unsupported":

                            answer = (
                                "I'm sorry, but I can only answer "
                                "questions related to the uploaded dataset."
                            )

                        elif is_simple_question(operation):

                            answer = factual_answer

                        else:

                            answer = explain_answer(
                                question,
                                factual_answer
                            )


        except Exception as e:

            print("\nError while processing question:")
            print(e)

            answer = (
                "Sorry, I couldn't process "
                "your question right now. "
                "Please try again."
            )


    # ---------------------------------
    # RENDER PAGE
    # ---------------------------------

    return render_template(

        "ask.html",

        question=question,

        answer=answer,

        filename=session["filename"]

    )

    
@app.route("/insights")
def insights():

    if "dataset_path" not in session:
        return redirect(url_for("home"))


    # ---------------------------------
    # LOAD DATASET
    # ---------------------------------

    df = pd.read_csv(
        session["dataset_path"]
    )


    # ---------------------------------
    # GENERAL FACTUAL INSIGHTS
    # ---------------------------------

    factual_insights, column_types = (
        generate_factual_insights(df)
    )


    # ---------------------------------
    # AI DATA ANALYSIS
    # ---------------------------------

    ai_analysis = generate_ai_insights(

        factual_insights,

        column_types

    )


    # ---------------------------------
    # DATA QUALITY
    # ---------------------------------

    quality_report = generate_quality_report(
        df
    )


    # ---------------------------------
    # OUTLIER DETECTION
    # ---------------------------------

    outliers = detect_outliers(
        df
    )


    # ---------------------------------
    # AI OUTLIER EXPLANATIONS
    # ---------------------------------

    ai_outlier_explanations = (
        generate_ai_outlier_explanations(
            outliers
        )
    )


    # ---------------------------------
    # RELATIONSHIP DETECTION
    # ---------------------------------

    relationship_findings = (
        detect_relationships(df)
    )


    # ---------------------------------
    # KEY FINDINGS
    # ---------------------------------

    key_findings = generate_key_findings(

        quality_report,

        outliers,

        relationship_findings,

        factual_insights

    )


    # ---------------------------------
    # TOP FINDINGS
    # ---------------------------------

    top_findings = get_top_findings(

        key_findings,

        limit=5

    )


    # ---------------------------------
    # AI KEY FINDINGS EXPLANATION
    # ---------------------------------

    ai_key_findings = (
        generate_ai_key_findings(
            top_findings
        )
    )


    # ---------------------------------
    # RENDER PAGE
    # ---------------------------------

    return render_template(

        "insights.html",

        factual_insights=factual_insights,

        ai_analysis=ai_analysis,

        outliers=outliers,

        ai_outlier_explanations=(
            ai_outlier_explanations
        ),

        relationship_findings=(
            relationship_findings
        ),

        key_findings=top_findings,

        ai_key_findings=ai_key_findings,

        filename=session["filename"]

    )

if __name__ == "__main__":
    app.run(debug=True)

