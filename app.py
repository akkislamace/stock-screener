import streamlit as st
import pandas as pd
import yfinance as yf
from src.database import init_db, SessionLocal, DimStock
from src.data_fetcher import update_database
from src.screener_logic import screen_stocks
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Screener", layout="wide")
st.title("📈 Stock Screener with SQL + Technical Indicators")

# Initialize database tables (only once)
init_db()

# Sidebar
with st.sidebar:
    st.header("Data Refresh")
    if st.button("🔄 Fetch Latest Data"):
        with st.spinner("Downloading data from Yahoo Finance..."):
            update_database()
        st.success("Database updated!")

    st.divider()
    st.header("Screening Filters")

    rsi_min = st.slider("Min RSI", 0, 100, 30)
    rsi_max = st.slider("Max RSI", 0, 100, 70)
    price_min = st.number_input("Min Price ($)", 0, 1000, 10)
    price_max = st.number_input("Max Price ($)", 0, 10000, 500)
    min_volume = st.number_input("Min Daily Volume", 0, 100_000_000, 1_000_000, step=100_000)
    sectors = ["All", "Technology", "Financial Services", "Healthcare", "Energy", "Consumer"]
    sector = st.selectbox("Sector", sectors)
    min_market_cap = st.number_input("Min Market Cap (Billion $)", 0.0, 2000.0, 10.0, step=1.0)

    run_screen = st.button("🔍 Run Screener")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    if run_screen:
        filters = {
            "min_rsi": rsi_min,
            "max_rsi": rsi_max,
            "min_price": price_min,
            "max_price": price_max,
            "min_volume": min_volume,
            "min_market_cap": min_market_cap,
        }
        if sector != "All":
            filters["sector"] = sector

        session = SessionLocal()
        results = screen_stocks(session, filters)
        session.close()

        if results:
            df = pd.DataFrame(results)
            st.subheader(f"Found {len(df)} stocks matching criteria")
            display_cols = ["symbol", "company_name", "sector", "close", "volume", "rsi", "sma_20", "sma_50"]
            st.dataframe(df[display_cols])
        else:
            st.info("No stocks match the current filters.")

with col2:
    st.subheader("Stock Chart")

    session = SessionLocal()
    stocks = session.query(DimStock).all()
    session.close()

    if stocks:
        selected = st.selectbox("Select a stock", [s.symbol for s in stocks])
        if selected:
            hist = yf.Ticker(selected).history(period="3mo")
            if not hist.empty:
                fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist["Close"], mode="lines")])
                fig.update_layout(
                    title=f"{selected} - Last 3 Months",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                latest_price = hist['Close'].iloc[-1]
                st.metric("Current Price", f"${latest_price:.2f}")
            else:
                st.warning("No price data available for this symbol.")
    else:
        st.info("No stocks in database. Click 'Fetch Latest Data' first.")

st.divider()
st.caption("📊 Data from Yahoo Finance | SQLite database | Built with Streamlit")