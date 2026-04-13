from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from pipeline.etl import run_etl
from crew.crew import run_crew

# -------------------------------
# ENV + PAGE CONFIG
# -------------------------------
load_dotenv()
st.set_page_config(
    page_title="AMACS - Automated Multi-Agent Audit & Compliance System",
    layout="wide",
)

# -------------------------------
# STYLES
# -------------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
      .stMetric { background: #111315; padding: 12px; border-radius: 10px; }
      .section-title { font-size: 1.1rem; font-weight: 600; color: #E5E7EB; }
      .section-subtle { color: #9CA3AF; font-size: 0.9rem; }
      .divider { border-top: 1px solid #1F2937; margin: 8px 0 16px 0; }
      .soft-card { background: #0f1113; padding: 14px; border-radius: 12px; border: 1px solid #1f2937; }
      .soft-card h4 { margin: 0 0 6px 0; }
      .soft-card p { margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# HELPERS
# -------------------------------

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "fraud_flag" not in df.columns:
        if "amount" in df.columns and "is_night" in df.columns:
            df["fraud_flag"] = ((df["amount"] > 500000) | (df["is_night"] == 1)).astype(int)
        else:
            df["fraud_flag"] = 0

    if "risk_score" not in df.columns:
        if "amount" in df.columns and df["amount"].max() != 0:
            df["risk_score"] = df["fraud_flag"] * 0.9 + (df["amount"] / df["amount"].max())
        else:
            df["risk_score"] = 0.0

    if "transaction_time" not in df.columns and "time" in df.columns:
        df["transaction_time"] = df["time"]

    return df


def safe_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series([0] * len(df), index=df.index)
    return pd.to_numeric(df[col], errors="coerce").fillna(0)


def kpi_row(df: pd.DataFrame):
    total = len(df)
    high_risk = int((safe_numeric(df, "risk_score") > st.session_state["risk_threshold"]).sum())
    fraud_pct = (safe_numeric(df, "fraud_flag").mean() * 100) if total else 0
    avg_value = safe_numeric(df, "amount").mean() if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transactions", f"{total}")
    c2.metric("High-Risk Transactions", f"{high_risk}")
    c3.metric("Fraud %", f"{fraud_pct:.2f}%")
    c4.metric("Avg Transaction Value", f"{avg_value:,.2f}")


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    search = st.text_input("Search by vendor / ID / keyword", "")
    if search:
        mask = df.astype(str).apply(lambda row: row.str.contains(search, case=False, na=False)).any(axis=1)
        df = df[mask]
    return df


def plot_risk_distribution(df: pd.DataFrame):
    scores = safe_numeric(df, "risk_score")
    fig, ax = plt.subplots()
    ax.hist(scores, bins=10, color="#93C5FD", edgecolor="#111827")
    ax.set_title("Risk Score Distribution")
    ax.set_xlabel("Risk Score")
    ax.set_ylabel("Count")
    st.pyplot(fig)


def plot_fraud_breakdown(df: pd.DataFrame):
    values = safe_numeric(df, "fraud_flag")
    counts = values.value_counts().sort_index()
    fig, ax = plt.subplots()
    ax.bar(["No Fraud", "Fraud"], [counts.get(0, 0), counts.get(1, 0)], color=["#6B7280", "#EF4444"])
    ax.set_title("Fraud Breakdown")
    ax.set_ylabel("Count")
    st.pyplot(fig)


def plot_time_analysis(df: pd.DataFrame):
    if "transaction_time" not in df.columns:
        st.info("No transaction time column available.")
        return

    temp = df.copy()
    temp["transaction_time"] = pd.to_datetime(temp["transaction_time"], errors="coerce")
    temp["hour"] = temp["transaction_time"].dt.hour
    hourly = temp.groupby("hour").size().reindex(range(24), fill_value=0)

    fig, ax = plt.subplots()
    ax.plot(hourly.index, hourly.values, color="#10B981")
    ax.set_title("Transactions by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Count")
    ax.set_xticks(range(0, 24, 2))
    st.pyplot(fig)


def high_risk_table(df: pd.DataFrame) -> pd.DataFrame:
    threshold = st.session_state["risk_threshold"]
    return df[safe_numeric(df, "risk_score") > threshold]


# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.markdown("## Controls")
st.sidebar.markdown("Upload data and configure audit settings")

uploaded_file = st.sidebar.file_uploader("Upload Transactions CSV", type=["csv"])

st.sidebar.slider(
    "Risk Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.05,
    key="risk_threshold",
)

st.sidebar.checkbox("Show Only High-Risk Transactions", key="show_only_high_risk")

run_btn = st.sidebar.button("Run Audit")

# -------------------------------
# MAIN LAYOUT
# -------------------------------
st.title("AMACS - Automated Multi-Agent Audit & Compliance System")
st.caption("Automated multi-agent audit analytics with compliance and fraud detection.")

if "audit_report" not in st.session_state:
    st.session_state["audit_report"] = ""

if uploaded_file:
    df = run_etl(uploaded_file)
    df = ensure_columns(df)

    # SECTION 1: KPIs
    st.markdown("<div class='section-title'>Overview KPIs</div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    kpi_row(df)

    # SECTION 2: Data Preview
    st.markdown("<div class='section-title'>Data Preview</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtle'>Cleaned transactions with search & filtering.</div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    filtered_df = filter_dataframe(df)

    if st.session_state["show_only_high_risk"]:
        filtered_df = high_risk_table(filtered_df)

    st.dataframe(filtered_df, use_container_width=True)

    # SECTION 3: Risk & Fraud Analytics
    st.markdown("<div class='section-title'>Risk & Fraud Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    a, b, c = st.columns(3)
    with a:
        plot_risk_distribution(df)
    with b:
        plot_fraud_breakdown(df)
    with c:
        plot_time_analysis(df)

    st.markdown("<div class='section-title'>High-Risk Transactions</div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    high_risk_df = high_risk_table(df)
    st.dataframe(high_risk_df, use_container_width=True)

    # SECTION 4: Audit Report
    st.markdown("<div class='section-title'>Audit Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    if run_btn:
        with st.spinner("Running multi-agent audit..."):
            st.session_state["audit_report"] = run_crew(df.to_json(orient="records"))
        st.success("Audit completed successfully.")

    if st.session_state["audit_report"]:
        with st.expander("View Audit Report", expanded=True):
            st.markdown(st.session_state["audit_report"])

        st.download_button(
            "Download Report",
            data=st.session_state["audit_report"],
            file_name="audit_report.md",
            mime="text/markdown",
        )

        if not high_risk_df.empty:
            st.download_button(
                "Download High-Risk CSV",
                data=high_risk_df.to_csv(index=False),
                file_name="high_risk_transactions.csv",
                mime="text/csv",
            )
else:
    st.info("Upload a CSV to begin the audit workflow.")
