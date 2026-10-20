
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import requests
import html

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="India Inflation Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "database": "india_inflation_intelligence",
}

CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#C3CEE0"},
    "margin": {"l": 12, "r": 12, "t": 45, "b": 12},
    "legend": {
        "orientation": "h",
        "yanchor": "bottom",
        "y": 1.02,
        "xanchor": "left",
        "x": 0,
    },
}

# =========================================================
# PREMIUM DARK THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(145deg, #080D18 0%, #0B1220 55%, #10172A 100%);
    color: #E5E7EB;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #0A1020;
    border-right: 1px solid #25334B;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #F8FAFC;
}

h1, h2, h3 {
    color: #F8FAFC !important;
    letter-spacing: -0.6px;
}

p, label, .stCaption {
    color: #A8B3C7;
}

.hero {
    background: linear-gradient(120deg, #142442, #111827 62%, #241B48);
    border: 1px solid #2B3E60;
    border-radius: 22px;
    padding: 32px;
    margin-bottom: 26px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.15);
}

.eyebrow {
    color: #8BB9FF;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    color: #F8FAFC;
    font-size: clamp(27px, 3vw, 38px);
    font-weight: 800;
    letter-spacing: -1.3px;
    line-height: 1.2;
    margin: 0;
}

.hero-subtitle {
    color: #B3C0D5;
    font-size: 14px;
    line-height: 1.7;
    margin-top: 12px;
}

.section-label {
    color: #8BB9FF;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-top: 10px;
}

.section-title {
    color: #F8FAFC;
    font-size: 22px;
    font-weight: 700;
    margin-top: 5px;
    margin-bottom: 17px;
}

.kpi-card {
    background: linear-gradient(145deg, #131F34, #0F1727);
    border: 1px solid #293B58;
    border-top: 3px solid #60A5FA;
    border-radius: 15px;
    padding: 18px 16px;
    min-height: 148px;
    height: 100%;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.kpi-label {
    color: #9AAAC3;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.6px;
    line-height: 1.5;
    margin-bottom: 15px;
}

.kpi-value {
    color: #F8FAFC;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -0.8px;
    overflow-wrap: anywhere;
    line-height: 1.3;
}

.kpi-note {
    color: #91A4C1;
    font-size: 10px;
    line-height: 1.5;
    margin-top: 10px;
    overflow-wrap: anywhere;
}

.panel {
    background: #101827;
    border: 1px solid #25334B;
    border-radius: 17px;
    padding: 20px;
}

.ai-panel {
    background: linear-gradient(135deg, #111D34, #19172F);
    border: 1px solid #34466A;
    border-radius: 19px;
    padding: 24px;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(100deg, #2563EB, #6366F1);
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    border: 1px solid #93C5FD;
    color: white;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #293B58;
    border-radius: 12px;
    overflow: hidden;
}

div[data-testid="stMetric"] {
    background: #111C30;
    border: 1px solid #293A56;
    border-radius: 14px;
    padding: 16px;
}

hr {
    border-color: #26334A;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "db_password" not in st.session_state:
    st.session_state.db_password = ""

if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

# =========================================================
# DATABASE
# =========================================================

@st.cache_data(ttl=60)
def load_data(password):
    connection = None

    try:
        connection = mysql.connector.connect(
            **DB_CONFIG,
            password=password,
        )

        query = """
            SELECT
                group_code,
                group_name,
                month,
                rural_index,
                urban_index,
                combined_index,
                rural_inflation,
                urban_inflation,
                combined_inflation
            FROM category_inflation
        """

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        return pd.DataFrame(records)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("## 📊 INFLATION IQ")
    st.caption("ECONOMIC INTELLIGENCE PLATFORM")
    st.divider()

    st.markdown("### Database connection")

    with st.form("database_connection"):
        password_input = st.text_input(
            "MySQL root password",
            type="password",
            value=st.session_state.db_password,
        )

        connect_clicked = st.form_submit_button(
            "Connect / Refresh",
            use_container_width=True,
        )

    if connect_clicked:
        st.session_state.db_password = password_input
        st.session_state.ai_report = None
        load_data.clear()
        st.rerun()

    st.divider()
    st.markdown("### Reporting period")
    st.markdown("**July 2026 → August 2026**")
    st.caption("Category-level CPI comparison")

    st.divider()
    st.markdown("### About this dashboard")
    st.caption(
        "Consumer price inflation analysis with "
        "SQL-backed data and local AI commentary."
    )
    st.caption("Python · MySQL · Plotly · Streamlit · Ollama")

# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">ECONOMIC DATA INTELLIGENCE / 2026</div>
    <div class="hero-title">India Inflation Intelligence</div>
    <div class="hero-subtitle">
        Explore category-level inflation movements, compare rural and
        urban price changes, and generate AI-assisted economic insights.
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.db_password:
    st.info(
        "Enter your MySQL root password in the sidebar "
        "and click Connect / Refresh."
    )
    st.stop()

# =========================================================
# LOAD AND VALIDATE DATA
# =========================================================

try:
    df = load_data(st.session_state.db_password)

except mysql.connector.Error as error:
    st.error(f"Could not connect to MySQL: {error}")
    st.info(
        "Check that the MySQL80 service is running "
        "and the password is correct."
    )
    st.stop()

except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

if df.empty:
    st.warning("The database returned no records.")
    st.stop()

df["month"] = df["month"].astype(str).str.strip()

numeric_columns = [
    "rural_index",
    "urban_index",
    "combined_index",
    "rural_inflation",
    "urban_inflation",
    "combined_inflation",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

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
    st.error(
        "No matching July and August categories found. "
        "Check the month values in your MySQL table."
    )
    st.stop()

comparison = pd.DataFrame({
    "group_name": august.loc[common_codes, "group_name"],
    "july_inflation": july.loc[common_codes, "combined_inflation"],
    "august_inflation": august.loc[common_codes, "combined_inflation"],
    "july_rural": july.loc[common_codes, "rural_inflation"],
    "august_rural": august.loc[common_codes, "rural_inflation"],
    "july_urban": july.loc[common_codes, "urban_inflation"],
    "august_urban": august.loc[common_codes, "urban_inflation"],
}).reset_index()

comparison = comparison.rename(columns={"index": "group_code"})

comparison["change_pp"] = (
    comparison["august_inflation"] - comparison["july_inflation"]
)

comparison["rural_urban_gap"] = (
    comparison["august_rural"] - comparison["august_urban"]
)

# =========================================================
# ANALYSIS CONTROLS
# =========================================================

st.markdown(
    '<div class="section-label">01 / EXPLORE</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Analysis controls</div>',
    unsafe_allow_html=True,
)

filter_col1, filter_col2 = st.columns([2, 1])

with filter_col1:
    search = st.text_input(
        "Search a category",
        placeholder="Try transport, electricity, personal care...",
    )

with filter_col2:
    direction = st.selectbox(
        "Inflation movement",
        ["All categories", "Increased", "Decreased", "Unchanged"],
    )

filtered = comparison.copy()

if search:
    filtered = filtered[
        filtered["group_name"].str.contains(
            search,
            case=False,
            na=False,
        )
    ]

if direction == "Increased":
    filtered = filtered[filtered["change_pp"] > 0]
elif direction == "Decreased":
    filtered = filtered[filtered["change_pp"] < 0]
elif direction == "Unchanged":
    filtered = filtered[filtered["change_pp"] == 0]

if filtered.empty:
    st.warning("No categories match the selected filters.")
    st.stop()

# =========================================================
# KPI CARDS - FIVE CARDS
# =========================================================

st.markdown(
    '<div class="section-label">02 / OVERVIEW</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Performance overview</div>',
    unsafe_allow_html=True,
)

# KPIs use the full comparison so filters do not change headline figures.
july_average = comparison["july_inflation"].mean()
august_average = comparison["august_inflation"].mean()
average_change = comparison["change_pp"].mean()

largest_increase = comparison.loc[
    comparison["change_pp"].idxmax()
]
largest_decrease = comparison.loc[
    comparison["change_pp"].idxmin()
]

kpi_columns = st.columns(5, gap="medium")

kpis = [
    {
        "label": "CATEGORIES ANALYSED",
        "value": f"{len(comparison)}",
        "note": "Matched across both months",
        "accent": "#60A5FA",
    },
    {
        "label": "JULY CATEGORY AVG.",
        "value": f"{july_average:.2f}%",
        "note": "Unweighted average",
        "accent": "#60A5FA",
    },
    {
        "label": "AUGUST CATEGORY AVG.",
        "value": f"{august_average:.2f}%",
        "note": f"{average_change:+.2f} pp vs July",
        "accent": "#A78BFA",
    },
    {
        "label": "LARGEST INCREASE",
        "value": f"{largest_increase['change_pp']:+.2f} pp",
        "note": str(largest_increase["group_name"]),
        "accent": "#F87171",
    },
    {
        "label": "LARGEST DECREASE",
        "value": f"{largest_decrease['change_pp']:+.2f} pp",
        "note": str(largest_decrease["group_name"]),
        "accent": "#34D399",
    },
]

for column, kpi in zip(kpi_columns, kpis):
    with column:
        st.markdown(
            f"""
            <div class="kpi-card"
                 style="border-top-color:{kpi['accent']};">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-note">
                    {html.escape(kpi['note'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption(
    "Category averages are unweighted and are not India's official "
    "headline inflation rate. Changes are expressed in percentage points."
)

# =========================================================
# MONTHLY COMPARISON
# =========================================================

st.divider()
st.markdown(
    '<div class="section-label">03 / MONTHLY MOVEMENT</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">July vs August</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns([1.2, 1])

with chart_col1:
    chart_data = filtered.melt(
        id_vars=["group_name"],
        value_vars=["july_inflation", "august_inflation"],
        var_name="Month",
        value_name="Inflation rate (%)",
    )

    chart_data["Month"] = chart_data["Month"].map({
        "july_inflation": "July 2026",
        "august_inflation": "August 2026",
    })

    fig = px.bar(
        chart_data,
        x="group_name",
        y="Inflation rate (%)",
        color="Month",
        barmode="group",
        color_discrete_map={
            "July 2026": "#60A5FA",
            "August 2026": "#A78BFA",
        },
        template="plotly_dark",
        hover_data={"Inflation rate (%)": ":.2f"},
    )

    fig.update_layout(
        **CHART_LAYOUT,
        height=450,
        xaxis_title="",
        yaxis_title="Inflation rate (%)",
    )
    fig.update_xaxes(tickangle=-45, showgrid=False)
    fig.update_yaxes(
        gridcolor="#25334A",
        zerolinecolor="#475569",
    )

    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    movement = filtered.sort_values("change_pp").copy()

    movement["Direction"] = movement["change_pp"].apply(
        lambda value: (
            "Increase" if value > 0
            else ("Decrease" if value < 0 else "Unchanged")
        )
    )

    fig2 = px.bar(
        movement,
        x="change_pp",
        y="group_name",
        orientation="h",
        color="Direction",
        color_discrete_map={
            "Increase": "#F87171",
            "Decrease": "#34D399",
            "Unchanged": "#94A3B8",
        },
        template="plotly_dark",
        hover_data={"change_pp": ":.2f"},
    )

    fig2.update_layout(
        **CHART_LAYOUT,
        height=450,
        xaxis_title="Change (percentage points)",
        yaxis_title="",
        showlegend=False,
    )
    fig2.update_xaxes(
        gridcolor="#25334A",
        zerolinecolor="#64748B",
    )
    fig2.update_yaxes(showgrid=False)

    st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# RURAL VS URBAN
# =========================================================

st.divider()
st.markdown(
    '<div class="section-label">04 / REGIONAL COMPARISON</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Rural vs urban inflation</div>',
    unsafe_allow_html=True,
)

regional = filtered.melt(
    id_vars=["group_code", "group_name"],
    value_vars=["august_rural", "august_urban"],
    var_name="Area",
    value_name="Inflation rate (%)",
)

regional["Area"] = regional["Area"].map({
    "august_rural": "Rural",
    "august_urban": "Urban",
})

fig3 = px.scatter(
    regional,
    x="Area",
    y="Inflation rate (%)",
    color="Area",
    hover_name="group_name",
    hover_data={"group_code": True, "Inflation rate (%)": ":.2f"},
    color_discrete_map={
        "Rural": "#60A5FA",
        "Urban": "#FBBF24",
    },
    template="plotly_dark",
)

fig3.update_traces(marker={"size": 10, "opacity": 0.8})
fig3.update_layout(
    **CHART_LAYOUT,
    height=390,
    xaxis_title="Area",
    yaxis_title="August inflation rate (%)",
)
fig3.update_yaxes(
    gridcolor="#25334A",
    zerolinecolor="#64748B",
)

st.plotly_chart(fig3, use_container_width=True)

gap_data = (
    filtered.assign(abs_gap=filtered["rural_urban_gap"].abs())
    .sort_values("abs_gap", ascending=False)
    .head(5)
)

st.markdown("#### Largest rural–urban gaps")

st.dataframe(
    gap_data[
        ["group_name", "august_rural", "august_urban", "rural_urban_gap"]
    ].rename(columns={
        "group_name": "Category",
        "august_rural": "Rural rate (%)",
        "august_urban": "Urban rate (%)",
        "rural_urban_gap": "Rural minus urban (pp)",
    }).round(2),
    use_container_width=True,
    hide_index=True,
)

# =========================================================
# AI INFLATION ANALYST
# =========================================================

st.divider()
st.markdown(
    '<div class="section-label">05 / INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="ai-panel">
    <div class="eyebrow">LOCAL AI · OLLAMA</div>
    <h2 style="margin:0;color:#F8FAFC;">AI Inflation Analyst</h2>
    <p style="color:#AAB7CD;margin-top:8px;line-height:1.7;">
        Generate a concise interpretation of observed movements,
        highlight important category changes, and flag values for verification.
    </p>
</div>
""", unsafe_allow_html=True)

if st.button("✦ Generate AI Insights", type="primary"):
    with st.spinner("Analyzing category-level changes with local AI..."):
        try:
            top_increases = (
                comparison.nlargest(5, "change_pp")[
                    [
                        "group_name",
                        "july_inflation",
                        "august_inflation",
                        "change_pp",
                    ]
                ]
                .round(2)
                .to_string(index=False)
            )

            top_decreases = (
                comparison.nsmallest(5, "change_pp")[
                    [
                        "group_name",
                        "july_inflation",
                        "august_inflation",
                        "change_pp",
                    ]
                ]
                .round(2)
                .to_string(index=False)
            )

            
            prompt = f"""
You are a professional business intelligence analyst reviewing
India's category-level inflation data.

Compare July 2026 with August 2026 using only the supplied data.

LARGEST INCREASES:
{top_increases}

LARGEST DECREASES:
{top_decreases}

Write a concise, professional report using these sections:

### 1. Executive Summary
Summarize the most important observed movements in 2-3 sentences.

### 2. Key Increases
Explain the largest increases. Include category names, July rates,
August rates, and changes in percentage points.

### 3. Key Decreases
Explain the largest decreases using the same numerical detail.
Do not exaggerate small changes.

### 4. Business Interpretation
Explain which movements may warrant monitoring.
Do not invent causes or claim unsupported business impacts.

### 5. Data Quality Checks
Flag extreme values and unusual movements for source verification.
Prioritize values that are unusually high relative to other categories.
Do not label every negative rate or small decrease as an error.
A suspicious value is not necessarily incorrect.

### 6. Limitations
These are category-level inflation rates, not India's official
headline inflation rate. Do not infer the overall inflation trend
from only the largest increases and decreases.

Rules:
- Use only the supplied figures.
- Express differences in percentage points (pp).
- Distinguish observations from interpretations.
- Never invent causes, news, or missing data.
- Keep the tone neutral, concise, and professional.
- Include all five supplied categories under Key Increases.
- Include all five supplied categories under Key Decreases.
- Preserve the exact figures and category names from the input.
- Never invent data-quality warnings or rank a category incorrectly.
- Flag Other personal effects (44.56% in August) for source verification
  because its value is unusually high relative to the other supplied rates.
- A negative inflation rate is not automatically a data error.
- Do not suggest causes such as supply chains, policies, or seasonality
  unless supporting evidence is explicitly provided.
- Do not describe August inflation as higher across most sectors
  unless the supplied data supports that statement.

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

            st.session_state.ai_report = (
                response.json()["response"].strip()
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to Ollama. Start Ollama and try again."
            )
        except requests.exceptions.Timeout:
            st.error("The AI request timed out. Try again.")
        except Exception as error:
            st.error(f"Could not generate AI insights: {error}")

if st.session_state.ai_report:
    st.markdown("### AI-generated analysis")
    st.markdown(st.session_state.ai_report)
    st.caption(
        "AI-generated commentary should be checked against source data "
        "before being used in a formal report."
    )

# =========================================================
# CATEGORY-LEVEL DATA EXPLORER
# =========================================================

st.divider()
st.markdown(
    '<div class="section-label">06 / DATA EXPLORER</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="section-title">Category-level data</div>',
    unsafe_allow_html=True,
)

display_columns = [
    "group_code",
    "group_name",
    "july_inflation",
    "august_inflation",
    "change_pp",
    "august_rural",
    "august_urban",
    "rural_urban_gap",
]

display_df = (
    filtered[display_columns]
    .sort_values("change_pp", ascending=False)
    .rename(columns={
        "group_code": "Code",
        "group_name": "Category",
        "july_inflation": "July (%)",
        "august_inflation": "August (%)",
        "change_pp": "Change (pp)",
        "august_rural": "Rural (%)",
        "august_urban": "Urban (%)",
        "rural_urban_gap": "Rural–urban gap (pp)",
    })
)

st.dataframe(
    display_df.round(2),
    use_container_width=True,
    hide_index=True,
    height=440,
)

csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download filtered data",
    data=csv_data,
    file_name="india_inflation_comparison.csv",
    mime="text/csv",
)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div style="text-align:center;padding:14px;color:#73839D;font-size:11px;line-height:1.8;">
    INDIA INFLATION INTELLIGENCE · CATEGORY-LEVEL CPI ANALYSIS · 2026
    <br>
    Built with Python, MySQL, Streamlit, Plotly and local AI.
</div>
""", unsafe_allow_html=True)
