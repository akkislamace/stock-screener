import yfinance as yf
import pandas as pd
from datetime import datetime
import logging
from src.database import SessionLocal, DimStock, DimDate, FactStockPrice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_stock_list():
    """Default list of stock symbols to track"""
    return [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "JPM", "BAC", "WFC",
        "JNJ", "PFE", "UNH",
        "XOM", "CVX", "NEE",
        "WMT", "PG", "KO", "PEP",
    ]


def fetch_fundamental_data(symbol):
    """Get company info (sector, market cap, etc.)"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            "symbol": symbol,
            "company_name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap"),
        }
    except Exception as e:
        logger.error(f"Fundamentals error for {symbol}: {e}")
        return None


def fetch_stock_data(symbol, start_date="2023-01-01"):
    """Get historical prices from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date)
        if data.empty:
            logger.warning(f"No data for {symbol}")
            return None
        data = data.reset_index()
        data = data.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        })
        data["ticker"] = symbol
        data["adj_close"] = data["close"]
        return data
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return None


def update_database(symbols=None, start_date="2023-01-01"):
    """Main pipeline: fetch and store data in SQLite"""
    if symbols is None:
        symbols = get_stock_list()

    session = SessionLocal()
    try:
        for symbol in symbols:
            logger.info(f"Processing {symbol}...")
            df = fetch_stock_data(symbol, start_date)
            if df is None:
                continue

            # Get or create stock record
            stock = session.query(DimStock).filter_by(symbol=symbol).first()
            if not stock:
                fundamentals = fetch_fundamental_data(symbol)
                stock = DimStock(
                    symbol=symbol,
                    company_name=fundamentals.get("company_name") if fundamentals else "",
                    sector=fundamentals.get("sector") if fundamentals else "",
                    industry=fundamentals.get("industry") if fundamentals else "",
                    market_cap=fundamentals.get("market_cap") if fundamentals else None,
                )
                session.add(stock)
                session.flush()

            # Process each row
            for _, row in df.iterrows():
                date = row["date"]
                date_id = int(date.strftime("%Y%m%d"))

                # Create date dimension if missing
                dim_date = session.query(DimDate).filter_by(date_id=date_id).first()
                if not dim_date:
                    dim_date = DimDate(
                        date_id=date_id,
                        full_date=date,
                        year=date.year,
                        month=date.month,
                        day=date.day,
                        quarter=(date.month - 1) // 3 + 1,
                        week=date.isocalendar()[1],
                        week_number=date.isocalendar()[1],
                        month_name=date.strftime("%B"),
                        is_weekend=date.weekday() >= 5,
                    )
                    session.add(dim_date)

                # Insert/update price fact
                fact = session.query(FactStockPrice).filter_by(
                    date_id=date_id, stock_id=stock.stock_id
                ).first()
                if fact:
                    fact.open = row["open"]
                    fact.high = row["high"]
                    fact.low = row["low"]
                    fact.close = row["close"]
                    fact.adj_close = row["adj_close"]
                    fact.volume = int(row["volume"]) if pd.notna(row["volume"]) else 0
                else:
                    fact = FactStockPrice(
                        date_id=date_id,
                        stock_id=stock.stock_id,
                        ticker=row["ticker"],
                        open=row["open"],
                        high=row["high"],
                        low=row["low"],
                        close=row["close"],
                        adj_close=row["adj_close"],
                        volume=int(row["volume"]) if pd.notna(row["volume"]) else 0,
                    )
                    session.add(fact)

            session.commit()
            logger.info(f"Completed {symbol}")
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
    finally:
        session.close()