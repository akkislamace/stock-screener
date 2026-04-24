# NSE Stock Screener

A Python + SQL + Streamlit application that screens 500+ NSE-listed 
stocks using financial filters, built to replicate core functionality 
of tools like Screener.in and Bloomberg terminal filters.

## What it does
- Filters stocks across 15+ financial metrics including YoY revenue 
  growth, profit growth, ROIC trends, and valuation multiples (P/E, P/B, EV/EBITDA)
- Interactive Streamlit UI for real-time filtering and multi-stock comparison
- SQL backend for efficient data storage and query-based screening logic
- Outputs a ranked, filterable table of qualifying stocks

## Financial concepts applied
- Return on Invested Capital (ROIC)
- Revenue and PAT growth (YoY)
- Valuation multiples: P/E, P/B, EV/EBITDA
- Liquidity filters: Current ratio, Debt/Equity

## Tech stack
- Python (pandas, Streamlit, matplotlib)
- SQL (SQLite — data storage and screener queries)
- Data: NSE-listed companies

## Project structure
