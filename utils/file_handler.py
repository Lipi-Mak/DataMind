import os
import pandas as pd
import uuid


def process_uploaded_file(
    file,
    upload_folder
):
    """
    Validates, saves and reads the uploaded CSV file.

    Returns:
        success (bool)
        data (dict)
    """

    # ---------------------------------
    # CHECK WHETHER FILE EXISTS
    # ---------------------------------

    if file is None:

        return False, {
            "error": "Please select a CSV file to upload."
        }


    # ---------------------------------
    # CHECK WHETHER FILENAME EXISTS
    # ---------------------------------

    if not file.filename:

        return False, {
            "error": "Please select a CSV file to upload."
        }


    # ---------------------------------
    # CHECK FILE EXTENSION
    # ---------------------------------

    if not file.filename.lower().endswith(
        ".csv"
    ):

        return False, {
            "error": "Please upload a CSV file."
        }

    # ---------------------------------
    # CREATE UPLOAD FOLDER
    # ---------------------------------

    os.makedirs(
        upload_folder,
        exist_ok=True
    )


    # ---------------------------------
    # CREATE FILE PATH
    # ---------------------------------

    unique_filename = (
        f"{uuid.uuid4().hex}_{file.filename}"
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )  

    # ---------------------------------
    # SAVE FILE
    # ---------------------------------

    try:

        file.save(
            filepath
        )

    except Exception:

        return False, {
            "error": (
                "The file could not be uploaded. "
                "Please try again."
            )
        }


    # ---------------------------------
    # READ CSV FILE
    # ---------------------------------

    try:

        df = pd.read_csv(
            filepath
        )

    except Exception:

        # Remove invalid uploaded file
        # if Pandas cannot read it.

        if os.path.exists(
            filepath
        ):

            os.remove(
                filepath
            )


        return False, {
            "error": (
                "The uploaded file could not be "
                "read as a valid CSV file."
            )
        }


    # ---------------------------------
    # CHECK EMPTY DATASET
    # ---------------------------------

    if df.empty:

        if os.path.exists(filepath):

            os.remove(filepath)

        return False, {
            "error": (
                "The uploaded CSV file is empty."
            )
        }


    # ---------------------------------
    # CHECK NO COLUMNS
    # ---------------------------------

    if len(df.columns) == 0:

        if os.path.exists(filepath):

            os.remove(filepath)

        return False, {
            "error": (
                "The uploaded CSV file does not contain any columns."
            )
        }


    # ---------------------------------
    # GET DATASET SHAPE
    # ---------------------------------

    rows, columns = df.shape


    # ---------------------------------
    # RETURN SUCCESS
    # ---------------------------------

    return True, {
        "rows": rows,
        "columns": columns,
        "filepath": filepath,
        "dataframe": df
    }