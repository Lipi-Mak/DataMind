import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def create_histogram(df, column_name):
    """
    Create a histogram for a numeric column.

    Parameters:
        df (DataFrame): Uploaded dataset
        column_name (str): Numeric column to visualize

    Returns:
        str: Relative path to the saved chart image
    """

    charts_folder = os.path.join("static", "charts")
    os.makedirs(charts_folder, exist_ok=True)

    plt.figure(figsize=(8, 5))

    df[column_name].dropna().hist(
        bins=15,
        edgecolor="black"
    )

    plt.title(f"{column_name} Distribution")
    plt.xlabel(column_name)
    plt.ylabel("Frequency")

    filename = f"{column_name.lower()}_histogram.png"
    filepath = os.path.join(charts_folder, filename)

    plt.savefig(filepath)
    plt.close()

    return filepath


def get_numeric_columns(df):
    """
    Return numeric columns that are suitable for visualization.

    ID-like columns are excluded because they do not represent
    meaningful continuous numerical data.
    """

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    visualizable_columns = []

    for column in numeric_columns:

        column_lower = column.lower()

        if (
            "id" in column_lower
            or column_lower.endswith("_id")
        ):
            continue

        visualizable_columns.append(column)

    return visualizable_columns


def get_visualizable_columns(df):
    """
    Return only the numeric columns that are useful
    for visualization.
    """

    numeric_columns = get_numeric_columns(df)

    ignored_keywords = [
        "id",
        "number",
        "no",
        "code"
    ]

    visualizable_columns = []

    for column in numeric_columns:

        column_lower = column.lower()

        should_ignore = False

        for keyword in ignored_keywords:

            if keyword in column_lower:
                should_ignore = True
                break

        if not should_ignore:
            visualizable_columns.append(column)

    return visualizable_columns

def create_all_histograms(df):
    """
    Create histograms for every visualizable numeric column.
    """

    visualizable_columns = get_visualizable_columns(df)

    chart_paths = []

    for column in visualizable_columns:

        chart_path = create_histogram(df, column)

        chart_paths.append(chart_path)

    return chart_paths

def create_boxplot(df, column_name):
    """
    Create a box plot for a numeric column.

    Parameters:
        df (DataFrame): Uploaded dataset
        column_name (str): Numeric column to visualize

    Returns:
        str: Relative path to the saved box plot image
    """

    charts_folder = os.path.join("static", "charts")
    os.makedirs(charts_folder, exist_ok=True)

    plt.figure(figsize=(8, 5))

    plt.boxplot(
        df[column_name].dropna()
    )

    plt.title(f"{column_name} Distribution - Box Plot")
    plt.ylabel(column_name)

    filename = f"{column_name.lower()}_boxplot.png"
    filepath = os.path.join(charts_folder, filename)

    plt.savefig(filepath)
    plt.close()

    return filepath


def create_all_boxplots(df):
    """
    Create box plots for every visualizable numeric column.
    """

    visualizable_columns = get_visualizable_columns(df)

    chart_paths = []

    for column in visualizable_columns:

        chart_path = create_boxplot(df, column)

        chart_paths.append(chart_path)

    return chart_paths


def create_correlation_heatmap(df):
    """
    Create a correlation heatmap for numeric columns.

    Parameters:
        df (DataFrame): Uploaded dataset

    Returns:
        str: Relative path to the saved heatmap image
    """

    charts_folder = os.path.join("static", "charts")
    os.makedirs(charts_folder, exist_ok=True)

    numeric_columns = get_visualizable_columns(df)

    if len(numeric_columns) < 2:
        return None

    correlation_matrix = df[numeric_columns].corr()

    plt.figure(figsize=(8, 6))

    plt.imshow(
        correlation_matrix,
        cmap="coolwarm",
        interpolation="nearest"
    )

    plt.colorbar()

    plt.xticks(
        range(len(numeric_columns)),
        numeric_columns,
        rotation=45,
        ha="right"
    )

    plt.yticks(
        range(len(numeric_columns)),
        numeric_columns
    )

    plt.title("Correlation Heatmap")

    plt.tight_layout()

    filename = "correlation_heatmap.png"
    filepath = os.path.join(charts_folder, filename)

    plt.savefig(filepath)
    plt.close()

    return filepath


def create_bar_chart(df, column_name):
    """
    Create a bar chart showing the frequency of each category.

    Parameters:
        df (DataFrame): Uploaded dataset
        column_name (str): Categorical column to visualize

    Returns:
        str: Relative path to the saved bar chart image
    """

    charts_folder = os.path.join("static", "charts")
    os.makedirs(charts_folder, exist_ok=True)

    value_counts = df[column_name].dropna().value_counts()

    plt.figure(figsize=(8, 5))

    value_counts.plot(
        kind="bar",
        edgecolor="black"
    )

    plt.title(f"{column_name} Distribution")
    plt.xlabel(column_name)
    plt.ylabel("Count")

    plt.xticks(rotation=45)

    plt.tight_layout()

    filename = f"{column_name.lower()}_bar_chart.png"
    filepath = os.path.join(charts_folder, filename)

    plt.savefig(filepath)
    plt.close()

    return filepath

def get_categorical_columns(df, max_unique_values=10):
    """
    Return categorical columns that are suitable for bar charts.

    Columns with too many unique values are ignored because
    they would create cluttered or unhelpful visualizations.
    """

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    visualizable_columns = []

    for column in categorical_columns:

        unique_count = df[column].nunique()
        total_count = len(df)

        if unique_count <= 1:
            continue

        if unique_count > max_unique_values:
            continue

        if unique_count / total_count > 0.8:
            continue

        visualizable_columns.append(column)

    return visualizable_columns


def create_all_bar_charts(df):
    """
    Create bar charts for all suitable categorical columns.
    """

    categorical_columns = get_categorical_columns(df)

    chart_paths = []

    for column in categorical_columns:

        chart_path = create_bar_chart(
            df,
            column
        )

        chart_paths.append(chart_path)

    return chart_paths


if __name__ == "__main__":
    print("Visualizer module loaded successfully.")