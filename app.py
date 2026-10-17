import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Investment Recommendation System", page_icon="📈", layout="wide")

DATA = Path(__file__).parent / "data" / "processed"
RISK_FREE = 0.07


@st.cache_data
def load_data():
    recs = pd.read_csv(DATA / "recommendations.csv", index_col=0)
    prices = pd.read_csv(DATA / "prices_close.csv", index_col=0, parse_dates=True)
    returns = pd.read_csv(DATA / "returns_daily.csv", index_col=0, parse_dates=True)
    return recs, prices, returns


def summarize(r):
    growth = (1 + r).cumprod()
    years = (r.index[-1] - r.index[0]).days / 365.25
    cagr = growth.iloc[-1] ** (1 / years) - 1
    vol = r.std() * (252 ** 0.5)
    dd = (growth / growth.cummax() - 1).min()
    return {
        "Annual return (CAGR %)": cagr * 100,
        "Volatility %": vol * 100,
        "Max drawdown %": dd * 100,
        "Sharpe": (cagr - RISK_FREE) / vol,
    }


recs, prices, returns = load_data()

st.title("📈 Investment Recommendation System")
st.caption(f"{len(recs)} Nifty 50 stocks · data from {prices.index[0]:%d %b %Y} to {prices.index[-1]:%d %b %Y}")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Stock Explorer", "Compare Stocks", "Portfolio Builder", "Risk vs Return"],
)

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

elif page == "Compare Stocks":
    st.subheader("Compare stocks")
    picks = st.multiselect(
        "Choose 2 to 5 stocks", list(recs.index),
        default=["ICICIBANK", "BHARTIARTL", "TCS"], max_selections=5,
    )
    if len(picks) < 2:
        st.info("Pick at least two stocks to compare.")
    else:
        norm = prices[picks] / prices[picks].iloc[0] * 100
        fig = px.line(norm, labels={"value": "Value of 100 invested", "index": "Date", "variable": "Stock"})
        fig.update_layout(height=450)
        st.plotly_chart(fig)

        cols = ["sector", "recommendation", "total_score", "risk_score",
                "cagr_%", "volatility_%", "max_drawdown_%", "beta", "sharpe"]
        st.dataframe(recs.loc[picks, cols])

elif page == "Portfolio Builder":
    st.subheader("Build an equal-weight portfolio")
    default = list(recs.index[recs["recommendation"] == "Buy"])
    picks = st.multiselect("Stocks in the portfolio", list(recs.index), default=default)
    if len(picks) == 0:
        st.info("Pick at least one stock.")
    else:
        port = returns[picks].mean(axis=1)
        market = returns["NIFTY50"]

        table = pd.DataFrame({"Your portfolio": summarize(port), "Nifty 50": summarize(market)}).round(2)
        st.dataframe(table)

        growth = pd.DataFrame({
            "Your portfolio": (1 + port).cumprod() * 100,
            "Nifty 50": (1 + market).cumprod() * 100,
        })
        fig = px.line(growth, labels={"value": "Value of 100 invested", "index": "Date", "variable": ""})
        fig.update_layout(height=450)
        st.plotly_chart(fig)

        mix = recs.loc[picks, "sector"].value_counts()
        st.write("**Sector mix**")
        st.plotly_chart(px.pie(values=mix.values, names=mix.index))
        st.caption("Past performance over this data window. The default picks were chosen using the same data, "
                   "so this is a demonstration, not a forecast.")

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