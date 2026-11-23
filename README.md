# DataMind

### Your AI Data Analyst

DataMind is a Streamlit application that helps people understand CSV datasets without writing code. Upload a dataset to explore its structure, data quality, visual patterns, statistical findings, relationships, and potential outliers.

DataMind follows a simple principle: **Python performs the factual analysis, while AI explains verified results.** This keeps calculations reproducible and reduces unsupported AI-generated claims.

## Features

- Upload CSV datasets through a simple interface
- View dataset size, columns, missing values, and duplicate rows
- Inspect a clean dataset preview and column information
- Check data quality and identify potential outliers using the IQR method
- Explore histograms, box plots, category charts, and correlation heatmaps
- Review factual insights and relationships between numerical variables
- Ask natural-language questions about the uploaded dataset
- Use Gemini to explain verified findings in beginner-friendly language

## How the AI works

DataMind does not ask the language model to perform the main calculations. Python and Pandas calculate the statistics first. Gemini receives the verified result and explains it in natural language.

Gemini is used only when the user selects an AI feature, such as **Explain these verified findings** or **Ask DataMind**. The app can still perform its factual analysis, tables, charts, and rule-based insights without an AI key.

## Technology stack

- Python
- Streamlit
- Pandas and NumPy
- Matplotlib
- Google Gemini API through `google-genai`
- Existing Flask/Ollama components retained for the original local version

## Run DataMind locally

### 1. Clone the repository

```bash
git clone https://github.com/Lipi-Mak/DataMind.git
cd DataMind
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Add the Gemini key locally

Create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

Never commit this file. It is already included in `.gitignore`.

### 5. Start the Streamlit app

```bash
python -m streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`.

## Using DataMind

1. Upload a CSV file.
2. Review the overview and dataset preview.
3. Open **Data quality** to inspect missing values and potential outliers.
4. Open **Visualizations** to explore generated charts.
5. Open **Insights** to review factual findings and relationships.
6. Open **Ask DataMind** to ask questions such as:

```text
What is the average salary?
Which department appears most frequently?
How many rows are in the dataset?
```

## Project structure

```text
DataMind/
├── streamlit_app.py          # Main Streamlit application
├── app.py                    # Original Flask entry point
├── requirements.txt
├── README.md
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml          # Local only; never commit
├── datasets/                 # Sample datasets
├── static/                   # Charts and styling assets
├── templates/                # Original Flask templates
├── utils/                    # Analysis and AI helpers
└── tests/                    # Automated tests
```

## Deployment

DataMind can be deployed for free using Streamlit Community Cloud:

1. Push the repository to GitHub.
2. Create a new Streamlit app from the repository.
3. Set the main file to `streamlit_app.py`.
4. Add `GEMINI_API_KEY` in the app’s Secrets settings.
5. Deploy and test with a sample CSV file.

The API key should be added through the deployment platform’s secret manager, not committed to GitHub.

## Design principles

- **Verified calculations first:** Python performs the calculations.
- **AI as an explainer:** Gemini explains results instead of inventing them.
- **Dataset-aware answers:** Ask DataMind focuses on the uploaded dataset.
- **Accessible analysis:** Common data-analysis workflows are available without Python or SQL.

## Author

**Lipi Makwana**  
GitHub: [Lipi-Mak](https://github.com/Lipi-Mak)
