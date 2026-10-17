import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Investment Recommendation System", page_icon="📈", layout="wide")

DATA = Path(__file__).parent / "data" / "processed"


@st.cache_data
def load_data():
    recs = pd.read_csv(DATA / "recommendations.csv", index_col=0)
    prices = pd.read_csv(DATA / "prices_close.csv", index_col=0, parse_dates=True)
    returns = pd.read_csv(DATA / "returns_daily.csv", index_col=0, parse_dates=True)
    return recs, prices, returns


recs, prices, returns = load_data()

st.title("📈 Investment Recommendation System")
st.caption(f"{len(recs)} Nifty 50 stocks · data from {prices.index[0]:%d %b %Y} to {prices.index[-1]:%d %b %Y}")

page = st.sidebar.radio("Go to", ["Overview", "Stock Explorer", "Risk vs Return"])

if page == "Overview":
    counts = recs["recommendation"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Stocks analysed", len(recs))
    c2.metric("Buy", int(counts.get("Buy", 0)))
    c3.metric("Hold", int(counts.get("Hold", 0)))
    c4.metric("Sell", int(counts.get("Sell", 0)))

    st.subheader("Recommendations")
    table = recs[["sector", "total_score", "recommendation", "risk_level", "trend", "reason"]]
    st.dataframe(table.sort_values("total_score", ascending=False))

elif page == "Stock Explorer":
    symbol = st.selectbox("Choose a stock", recs.index)
    row = recs.loc[symbol]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recommendation", row["recommendation"])
    c2.metric("Total score", f"{row['total_score']:.1f}")
    c3.metric("Risk level", f"{row['risk_level']} ({row['risk_score']:.0f})")
    c4.metric("Trend", row["trend"])
    st.write(f"**Why:** {row['reason']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Annual return (CAGR)", f"{row['cagr_%']:.1f}%")
    c2.metric("Volatility", f"{row['volatility_%']:.1f}%")
    c3.metric("Max drawdown", f"{row['max_drawdown_%']:.1f}%")
    c4.metric("Beta / Sharpe", f"{row['beta']:.2f} / {row['sharpe']:.2f}")

    s = prices[symbol]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s, name="Price"))
    fig.add_trace(go.Scatter(x=s.index, y=s.rolling(50).mean(), name="50-day average"))
    fig.add_trace(go.Scatter(x=s.index, y=s.rolling(200).mean(), name="200-day average"))
    fig.update_layout(title=f"{symbol} price", height=450)
    st.plotly_chart(fig)

elif page == "Risk vs Return":
    st.subheader("Risk vs return")
    color_by = st.radio("Colour by", ["recommendation", "risk_level"], horizontal=True)
    fig = px.scatter(
        recs.reset_index(names="stock"),
        x="risk_score", y="cagr_%", color=color_by, text="stock",
        hover_name="stock", hover_data=["sector", "sharpe", "total_score"],
        color_discrete_map={"Buy": "green", "Hold": "orange", "Sell": "red",
                            "Low": "green", "Medium": "orange", "High": "red"},
        labels={"risk_score": "Risk score (0 = safest)", "cagr_%": "Annual return (CAGR %)"},
    )
    fig.update_traces(textposition="top center", marker_size=10)
    fig.add_hline(y=0, line_color="grey")
    fig.update_layout(height=600)
    st.plotly_chart(fig)

st.divider()
st.caption("For education only. Not financial advice.")