from flask import Flask, render_template, request
import os
import pandas as pd

app = Flask(__name__)

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

            return render_template(
                "index.html",
                success=True,
                rows=result["rows"],
                columns=result["columns"]
            )

        return render_template(
           "index.html",
            error=result["error"]
        )


if __name__ == "__main__":
    app.run(debug=True)