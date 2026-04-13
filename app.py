from dotenv import load_dotenv
import os

load_dotenv()

# Use the same key name as llm.py / .env
print("API KEY SET:", bool(os.getenv("OPENROUTER_API_KEY")))  # Debug (no secret)
import streamlit as st
from pipeline.etl import run_etl
from crew.crew import run_crew



st.title("🧾 Automated Audit System (AMACS)")

uploaded_file = st.file_uploader("Upload Transactions CSV")

if uploaded_file:
    df = run_etl(uploaded_file)

    st.write("### Cleaned Data")
    st.dataframe(df)

    if st.button("Run Audit"):
        result = run_crew(df.to_string())

        st.write("### Audit Report")
        st.write(result)
