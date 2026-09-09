# DataMind

### Your AI Data Analyst

DataMind is a Flask-based web application that helps users understand CSV datasets through automated data analysis, visualizations, statistical findings, and natural-language explanations.

Instead of requiring users to manually inspect a dataset, DataMind organizes the analysis into a simple workflow: upload a CSV, understand its structure and quality, explore visual patterns, review important findings, and ask questions about the data.

The application uses Python for factual and statistical analysis and a locally running Ollama model for natural-language explanations.

---

## Overview

Data analysis often requires switching between spreadsheets, Python scripts, visualization tools, and statistical methods just to answer basic questions about a dataset.

DataMind brings these steps together into one interface.

The application:

1. Accepts a CSV dataset
2. Profiles the dataset
3. Checks data quality
4. Generates visualizations
5. Detects important findings and unusual values
6. Identifies relationships between numerical variables
7. Uses local AI to explain verified findings
8. Allows users to ask questions about their dataset

A key design principle is that **Python performs the actual calculations while the AI explains the results**. This helps prevent the language model from inventing statistics or performing unsupported calculations.

---

## Features

### Dataset Upload

Upload a CSV file directly through the web interface.

DataMind processes the uploaded dataset and maintains the active dataset throughout the analysis workflow.

### Dataset Overview

Automatically summarizes the structure of the uploaded dataset, including information about its rows, columns, and data characteristics.

### Data Quality Analysis

Analyzes common data-quality issues such as:

* Missing values
* Duplicate rows
* Column characteristics
* Dataset completeness

### Automated Visualizations

Generates visualizations based on the available data, including:

* Histograms
* Box plots
* Bar charts
* Correlation heatmaps

The visualization system adapts to the columns available in the uploaded dataset.

### Automated Insights

DataMind generates factual observations directly from the dataset.

These include:

* Dataset size
* Missing-value information
* Duplicate-row information
* Numerical summaries
* Common categorical values
* Column classifications

### Outlier Detection

Numerical columns are analyzed for potential outliers using the Interquartile Range (IQR) method.

DataMind reports the detected values and relevant statistical boundaries.

### Relationship Detection

DataMind analyzes numerical variables for relationships using correlation analysis.

Detected relationships include:

* Variables involved
* Correlation value
* Relationship direction
* Relationship strength

### AI-Powered Explanations

DataMind uses a locally running Ollama model to turn verified statistical findings into concise, beginner-friendly explanations.

The AI is intentionally constrained to the results calculated by Python.

It is instructed not to:

* Invent statistics
* Change numerical results
* Perform new calculations
* Treat correlation as causation
* Introduce unsupported conclusions

This creates a separation between **data computation** and **natural-language explanation**.

### Ask DataMind

Users can ask questions about their uploaded dataset using natural language.

DataMind:

1. Determines whether the question is relevant to the dataset
2. Interprets the requested operation
3. Performs the calculation using Python
4. Returns the factual result
5. Uses Ollama to explain the result when appropriate

Questions unrelated to the uploaded dataset are rejected rather than answered using unsupported information.

---

## Application Workflow

```text
                 CSV Upload
                     |
                     v
              Dataset Overview
                     |
                     v
              Data Quality Check
                     |
                     v
               Visualizations
                     |
                     v
              Automated Insights
                     |
          +----------+----------+
          |                     |
          v                     v
    Detected Findings      Ask DataMind
          |                     |
          +----------+----------+
                     |
                     v
             Local AI Explanation
```

---

## AI Architecture

DataMind follows a **Python-first, AI-second** approach.

```text
                    User Dataset
                         |
                         v
                 Python / Pandas
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Statistics   Outliers   Relationships
             |           |           |
             +-----------+-----------+
                         |
                         v
                 Verified Findings
                         |
                         v
                    Ollama LLM
                         |
                         v
              Natural-Language Explanation
```

The language model does not serve as the primary source of numerical truth.

Instead, Python performs the analysis first. The resulting findings are then provided to Ollama for explanation.

This architecture makes the AI component more controlled and reduces the risk of unsupported numerical claims.

---

## Technology Stack

### Backend

* Python
* Flask
* Pandas
* NumPy

### Data Analysis

* Pandas
* NumPy
* Statistical analysis
* IQR-based outlier detection
* Correlation analysis

### Visualization

* Matplotlib

### AI

* Ollama
* Llama 3.2 3B
* Local inference

### Frontend

* HTML
* Jinja2
* CSS
* Bootstrap Icons

### Testing

* Python test suite
* Dedicated tests for AI-related functionality
* Outlier detection tests
* Relationship detection tests
* Key-finding tests
* Understanding/question-processing tests

---

## Project Structure

```text
DataMind/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── datasets/
│   └── employees.csv
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── overview.html
│   ├── quality.html
│   ├── visualizations.html
│   ├── insights.html
│   ├── ask.html
│   └── error.html
│
├── static/
│   ├── css/
│   │   └── datamind.css
│   └── charts/
│
├── utils/
│   ├── analyzer.py
│   ├── ai_engine.py
│   ├── file_handler.py
│   ├── insight_generator.py
│   ├── key_findings.py
│   ├── outlier_detector.py
│   ├── quality_checker.py
│   ├── question_answerer.py
│   ├── relationship_detector.py
│   ├── report_generator.py
│   └── visualizer.py
│
└── tests/
    ├── test_ai_key_findings.py
    ├── test_ai_relationships.py
    ├── test_explanation.py
    ├── test_key_findings.py
    ├── test_ollama.py
    ├── test_outliers.py
    ├── test_relationships.py
    └── test_understanding.py
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Lipi-Mak/DataMind.git
cd DataMind
```

### 2. Create a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama separately on your system.

Then download the model used by DataMind:

```bash
ollama pull llama3.2:3b
```

If Ollama is not already running, start its local server:

```bash
ollama serve
```

Keep the Ollama process running while using the AI-powered features of DataMind.

### 5. Start DataMind

Open another terminal with the virtual environment activated:

```bash
python app.py
```

Then open the local Flask address shown in your terminal.

---

## Using DataMind

### Step 1 — Upload a Dataset

Start with a CSV file containing the data you want to analyze.

A sample dataset is included in:

```text
datasets/employees.csv
```

### Step 2 — Review the Dataset

DataMind first provides an overview of the dataset and its structure.

### Step 3 — Check Data Quality

Review missing values, duplicate records, and other basic quality information.

### Step 4 — Explore Visualizations

Use automatically generated charts to explore distributions, categorical values, outliers, and numerical relationships.

### Step 5 — Review Insights

DataMind combines factual analysis, outlier detection, relationship detection, and prioritized findings.

### Step 6 — Ask DataMind

Ask natural-language questions about the uploaded dataset.

For example:

```text
What is the average salary?
```

```text
Which department appears most frequently?
```

```text
How many rows are in the dataset?
```

The factual answer is calculated from the dataset before the AI generates an explanation.

---

## Testing

The repository contains tests covering several components of the analysis and AI pipeline.

Run the test suite with:

```bash
pytest
```

For a more verbose output:

```bash
pytest -v
```

---

## Design Principles

### 1. Factual analysis before AI

Numerical calculations and statistical findings are generated programmatically rather than relying on an LLM.

### 2. Local AI

Ollama allows the AI functionality to run locally without requiring a paid external AI API.

### 3. Dataset-aware responses

Ask DataMind is designed to answer questions about the currently uploaded dataset rather than acting as a general-purpose chatbot.

### 4. Explainability

AI-generated responses are based on findings already calculated by the analysis pipeline.

### 5. Simplicity

The interface is designed to make common data-analysis tasks accessible without requiring users to write Python or SQL.

---

## Current Limitations

DataMind is currently designed for CSV-based exploratory data analysis.

Some limitations include:

* The application currently focuses on CSV datasets.
* AI-powered features require a locally installed Ollama model.
* The supported question types are limited to operations implemented by the question-answering system.
* Statistical findings are intended for exploratory analysis rather than formal statistical inference.
* Correlation findings represent association and should not be interpreted as causation.

---

## Future Improvements

Potential future development areas include:

* More advanced dataset profiling
* Additional visualization types
* Expanded natural-language question support
* Improved handling of larger datasets
* More configurable AI models
* Exportable analysis reports
* Additional automated statistical tests
* Deployment support

---

## Project Goal

DataMind was built to explore how traditional data-analysis workflows can be combined with local AI to create a more accessible and explainable data-analysis experience.

The project focuses on an important distinction:

> **AI should help explain data analysis, not replace the underlying analysis.**

---

## Author

**Lipi Makwana**

Data Science student interested in data analysis, AI, and practical software projects.

GitHub: [Lipi-Mak](https://github.com/Lipi-Mak)
