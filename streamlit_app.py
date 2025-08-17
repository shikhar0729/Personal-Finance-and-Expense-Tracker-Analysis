import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
from src.etl import load_and_standardize_csv, auto_categorize
from src.analytics import summary_kpis, monthly_trend, by_category, top_merchants, detect_recurring, anomaly_spend
import plotly.express as px

st.set_page_config(page_title="Personal Finance & Expense Tracker", layout="wide")
st.title("💸 Personal Finance & Expense Tracker Analysis")

st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

@st.cache_data(show_spinner=False)
def _process(content: bytes) -> pd.DataFrame:
    s = StringIO(content.decode("utf-8"))
    df = load_and_standardize_csv(s)
    df = auto_categorize(df)
    return df

if "df" not in st.session_state:
    st.session_state.df = None

if uploaded is not None:
    st.session_state.df = _process(uploaded.getvalue())

st.sidebar.write("Or use sample:")
if st.sidebar.button("Load Sample"):
    with open("data/sample_transactions.csv", "rb") as f:
        st.session_state.df = _process(f.read())

if st.session_state.df is None:
    st.info("Upload a CSV to get started, or click **Load Sample** from the sidebar.")
    st.stop()

df = st.session_state.df.copy()

st.subheader("Quick Summary")
kpis = summary_kpis(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Income", f"₹{kpis['income']:,.0f}")
c2.metric("Total Expense", f"₹{kpis['expense']:,.0f}")
c3.metric("Net Savings", f"₹{kpis['net']:,.0f}")
c4.metric("Savings Rate", f"{kpis['savings_rate']:.1f}%")

st.subheader("Trends & Breakdown")

m = monthly_trend(df)
fig_line = px.line(m, x="month", y=["income","expense","net"], markers=True)
st.plotly_chart(fig_line, use_container_width=True)

cat = by_category(df)
fig_bar = px.bar(cat, x="category", y="expense")
st.plotly_chart(fig_bar, use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    tm = top_merchants(df, n=10)
    st.markdown("**Top Merchants (Expense)**")
    st.dataframe(tm, use_container_width=True)
with c6:
    rec = detect_recurring(df)
    st.markdown("**Likely Recurring Charges**")
    st.dataframe(rec, use_container_width=True)

st.subheader("Anomaly Detection")
anom = anomaly_spend(df)
if anom.empty:
    st.success("No significant monthly anomalies detected.")
else:
    st.warning("Unusual monthly spend detected:")
    st.dataframe(anom, use_container_width=True)

st.subheader("Transactions")
st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

st.download_button(
    label="⬇️ Download Cleaned CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="cleaned_transactions.csv",
    mime="text/csv"
)
