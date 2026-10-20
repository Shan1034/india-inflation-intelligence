
import mysql.connector
import pandas as pd
import requests
from getpass import getpass


# ---------------- CONFIGURATION ----------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "database": "india_inflation_intelligence",
}


# ---------------- LOAD DATA ----------------

def load_inflation_data():
    password = getpass("MySQL root password: ")
    connection = None

    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            password=password,
        )

        query = """
            SELECT group_code, group_name, month,
                   rural_inflation, urban_inflation,
                   combined_inflation
            FROM category_inflation
        """

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        return pd.DataFrame(rows)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


# ---------------- DATA ANALYSIS ----------------

def create_comparison(df):
    df["month"] = df["month"].astype(str).str.strip()

    july = (
        df[df["month"] == "July-2026"]
        .drop_duplicates("group_code")
        .set_index("group_code")
    )

    august = (
        df[df["month"] == "August-2026"]
        .drop_duplicates("group_code")
        .set_index("group_code")
    )

    common_codes = july.index.intersection(august.index)

    if len(common_codes) == 0:
        raise ValueError(
            "No matching July/August categories. "
            "Check the month values in MySQL."
        )

    comparison = pd.DataFrame({
        "group_name": august.loc[common_codes, "group_name"],
        "july_inflation": pd.to_numeric(
            july.loc[common_codes, "combined_inflation"]
        ),
        "august_inflation": pd.to_numeric(
            august.loc[common_codes, "combined_inflation"]
        ),
        "july_rural": pd.to_numeric(
            july.loc[common_codes, "rural_inflation"]
        ),
        "august_rural": pd.to_numeric(
            august.loc[common_codes, "rural_inflation"]
        ),
        "july_urban": pd.to_numeric(
            july.loc[common_codes, "urban_inflation"]
        ),
        "august_urban": pd.to_numeric(
            august.loc[common_codes, "urban_inflation"]
        ),
    })

    comparison["change_pp"] = (
        comparison["august_inflation"]
        - comparison["july_inflation"]
    )

    return comparison.sort_values(
        "change_pp", ascending=False
    )


def show_analysis(comparison):
    print("\n" + "=" * 60)
    print("INDIA INFLATION INTELLIGENCE")
    print("July 2026 vs August 2026")
    print("=" * 60)

    print(f"\nCategories compared: {len(comparison)}")

    print("\nTOP 5 INFLATION INCREASES")
    print("-" * 60)
    print(
        comparison.head(5)[
            ["group_name", "july_inflation",
             "august_inflation", "change_pp"]
        ].round(2).to_string(index=False)
    )

    print("\nTOP 5 INFLATION DECREASES")
    print("-" * 60)
    print(
        comparison.tail(5).sort_values("change_pp")[
            ["group_name", "july_inflation",
             "august_inflation", "change_pp"]
        ].round(2).to_string(index=False)
    )

    print("\nAVERAGE CATEGORY RATE (UNWEIGHTED)")
    print("-" * 60)
    print(
        "July:",
        round(comparison["july_inflation"].mean(), 2), "%"
    )
    print(
        "August:",
        round(comparison["august_inflation"].mean(), 2), "%"
    )
    print(
        "Change:",
        round(comparison["change_pp"].mean(), 2),
        "percentage points"
    )
    print("Note: This is NOT India's official headline inflation rate.")


# ---------------- LOCAL AI ANALYST ----------------


def generate_ai_insight(comparison):
    top_increases = comparison.head(5)[
        ["group_name", "july_inflation", "august_inflation", "change_pp"]
    ].round(2).to_string(index=False)

    top_decreases = comparison.tail(5).sort_values(
        "change_pp"
    )[
        ["group_name", "july_inflation", "august_inflation", "change_pp"]
    ].round(2).to_string(index=False)

    prompt = f"""
You are a professional business intelligence analyst reviewing
category-level inflation data for India.

Compare July 2026 with August 2026 using only the supplied data.

TOP INCREASES:
{top_increases}

TOP DECREASES:
{top_decreases}

Write a concise report with these sections:

1. EXECUTIVE SUMMARY
Summarize the most important observed movements in 2-3 sentences.

2. KEY INCREASES
Include category names, July rates, August rates, and changes in pp.

3. KEY DECREASES
Include category names, July rates, August rates, and changes in pp.
Do not exaggerate small changes.

4. BUSINESS INTERPRETATION
Explain what movements may warrant monitoring.
Do not invent causes or claim unsupported business impacts.

5. DATA QUALITY CHECKS
Flag extreme values and unusual movements for source verification.
Do not label every small change as a data-quality issue.
A suspicious value is not necessarily incorrect.

6. LIMITATIONS
These are category-level rates, not India's official headline
inflation rate. An unweighted average of category rates is not
the official headline inflation rate.

Rules:
- Use only the supplied figures.
- Changes are measured in percentage points (pp).
- Separate observed facts from interpretation.
- Keep the report concise, neutral, and professional.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=240,
    )

    response.raise_for_status()
    result = response.json()

    if "response" not in result:
        raise RuntimeError(f"Unexpected Ollama response: {result}")

    return result["response"].strip()

# ---------------- MAIN PROGRAM ----------------

def main():
    try:
        print("\nConnecting to MySQL and loading data...")
        df = load_inflation_data()

        if df.empty:
            print("No data found in the database.")
            return

        print(f"Records loaded: {len(df)}")

        comparison = create_comparison(df)
        show_analysis(comparison)

        print("\n" + "=" * 60)
        print("AI-GENERATED INSIGHTS")
        print("=" * 60)
        print("Generating insights with local Ollama AI...\n")

        insights = generate_ai_insight(comparison)
        print(insights)

        print("\n" + "=" * 60)
        print("Analysis completed successfully.")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to Ollama.")
        print("Make sure Ollama is running on your computer.")

    except requests.exceptions.Timeout:
        print("\nERROR: Ollama took too long to respond.")
        print("Try again after the model has loaded.")

    except requests.exceptions.RequestException as error:
        print(f"\nOllama request failed: {error}")

    except mysql.connector.Error as error:
        print(f"\nMySQL connection/query failed: {error}")

    except (ValueError, KeyError) as error:
        print(f"\nData validation error: {error}")


if __name__ == "__main__":
    main()
