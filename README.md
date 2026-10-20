\# India Inflation Intelligence



An interactive data analytics project that compares category-level Consumer Price Index (CPI) inflation across July and August 2026 using Python, MySQL, Streamlit, Plotly, and a locally hosted AI model.



\## Project Overview



India Inflation Intelligence helps explore changes in category-level inflation rates through an interactive dashboard and AI-generated commentary.



The project combines data processing, SQL-based analysis, interactive visualizations, and a local AI assistant.



\## Key Features



\- \*\*Data processing:\*\* Loads and prepares monthly CPI category data.

\- \*\*MySQL integration:\*\* Stores and retrieves category-level inflation records.

\- \*\*Interactive dashboard:\*\* Displays key metrics, monthly comparisons, and rural-versus-urban analysis.

\- \*\*Inflation comparison:\*\* Calculates changes between July and August 2026 in percentage points.

\- \*\*AI-assisted insights:\*\* Uses Ollama with the Qwen2.5 3B model to generate explanatory commentary.

\- \*\*Data validation:\*\* Checks category matching, duplicate records, and calculation consistency.



\## Technology Stack



\- Python

\- Pandas

\- MySQL

\- Streamlit

\- Plotly

\- Ollama — Qwen2.5 3B

\- SQL



\## Selected Findings



Based on the current processed dataset:



\- The largest category-level increase was in \*\*Transport services for goods\*\*, rising from 7.77% to 14.64% (+6.87 percentage points).

\- The largest category-level decrease was in \*\*Alcoholic beverages\*\*, falling from 2.35% to 1.97% (−0.38 percentage points).

\- The unweighted average category rate was 3.52% in July and 3.92% in August.



\*\*Important:\*\* These averages are unweighted averages of category-level inflation rates. They are not India's official headline inflation rates. The observations describe the supplied data and do not establish the causes of the changes.



\## Data Validation



The following checks have passed:



\- 86 records in the CSV and 86 records in MySQL.

\- No unmatched category-month records after normalizing category-code formatting.

\- No field mismatches between the processed CSV and MySQL for the fields compared.

\- All 43 July-to-August category changes match the calculated differences.

\- No duplicate category codes in the monthly comparison dataset.

\- The reported values for “Other personal effects” match the corresponding July and August source Excel files.



These checks establish consistency within the tested pipeline; they do not independently certify every value in the original source data.



\## Project Structure



```text

india-inflation-intelligence/

├── ai/

│   └── ai\_analyst.py

├── report/

│   ├── compare\_inflation.py

│   └── report/

│       └── import\_data.py

├── sql/

│   └── inflation\_analysis.sql

├── clean\_data.py

├── dashboard.py

├── requirements.txt

└── .gitignore

```



\## Run Locally



1\. Install Python and MySQL.

2\. Create and activate a Python virtual environment.

3\. Install the dependencies:



&#x20;  ```bash

&#x20;  pip install -r requirements.txt

&#x20;  ```



4\. Create the `india\_inflation\_intelligence` MySQL database and import the CPI data using the project's import workflow.

5\. Configure your local database connection. Do not commit passwords or other secrets.

6\. Install and start Ollama, then download the model:



&#x20;  ```bash

&#x20;  ollama pull qwen2.5:3b

&#x20;  ```



7\. Launch the dashboard from the project root:



&#x20;  ```bash

&#x20;  streamlit run dashboard.py

&#x20;  ```



Follow the database configuration in the application code and ensure the required tables and data are available before launching the dashboard.



\## Limitations



\- The current comparison covers July and August 2026 only.

\- AI-generated commentary may omit details or make mistakes; verify its statements against the underlying data.

\- Category-level rates and unweighted category averages should not be interpreted as the official headline inflation rate.

\- The project’s validation checks focus on data consistency and calculation correctness within the tested workflow.



\## Future Improvements



\- Add automated data-quality tests.

\- Expand the analysis to additional months.

\- Improve reproducibility of the data import workflow.

\- Add automated tests for dashboard metrics and AI-generated claims.



\## License



No license has been selected yet. Add a license before permitting reuse under specified terms.

