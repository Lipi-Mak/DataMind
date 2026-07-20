from flask import Flask, render_template, request, session, redirect, url_for
import os
import pandas as pd

from utils.file_handler import process_uploaded_file
from utils.analyzer import get_dataset_overview
from utils.quality_checker import generate_quality_report

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)