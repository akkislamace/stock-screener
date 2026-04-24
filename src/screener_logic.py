from sqlalchemy import func
from src.database import SessionLocal, DimStock, DimDate, FactStockPrice
from src.indicators import add_all_indicators
import pandas as pd


def get_latest_date(session):
    latest = session.query(DimDate).order_by(DimDate.full_date.desc()).first()
    return latest.full_date if latest else None


def get_stock_data_with_indicators(session, symbol, lookback=100):
    """Return a DataFrame with price + indicators for a single stock"""
    stock = session.query(DimStock).filter_by(symbol=symbol).first()
    if not stock:
        return None

    prices = session.query(FactStockPrice).filter_by(stock_id=stock.stock_id)\
        .order_by(FactStockPrice.date_id.desc()).limit(lookback).all()

    if not prices:
        return None

    df = pd.DataFrame([{
        "date": p.date_id,
        "close": p.close,
        "high": p.high,
        "low": p.low,
        "volume": p.volume
    } for p in prices])
    df = df.sort_values("date")
    df = add_all_indicators(df)
    latest_row = df.iloc[-1]
    return {
        "symbol": symbol,
        "company_name": stock.company_name,
        "sector": stock.sector,
        "market_cap": stock.market_cap,
        "close": latest_row["close"],
        "volume": latest_row["volume"],
        "rsi": latest_row["rsi"],
        "sma_20": latest_row["sma_20"],
        "sma_50": latest_row["sma_50"],
        "macd": latest_row["macd"],
        "macd_signal": latest_row["macd_signal"],
    }


def screen_stocks(session, filters):
    """
    filters = {
        "min_rsi": 30,
        "max_rsi": 70,
        "min_price": 10,
        "max_price": 500,
        "min_volume": 1000000,
        "sector": "Technology",
        "min_market_cap": 10  # billions
    }
    """
    # Get all distinct symbols from dim_stocks
    all_symbols = [s[0] for s in session.query(DimStock.symbol).all()]

    results = []
    for symbol in all_symbols:
        data = get_stock_data_with_indicators(session, symbol)
        if not data:
            continue

        # Apply filters
        if filters.get("min_rsi") and data["rsi"] and data["rsi"] < filters["min_rsi"]:
            continue
        if filters.get("max_rsi") and data["rsi"] and data["rsi"] > filters["max_rsi"]:
            continue
        if filters.get("min_price") and data["close"] < filters["min_price"]:
            continue
        if filters.get("max_price") and data["close"] > filters["max_price"]:
            continue
        if filters.get("min_volume") and data["volume"] < filters["min_volume"]:
            continue
        if filters.get("sector") and data["sector"] != filters["sector"]:
            continue
        if filters.get("min_market_cap"):
            cap_billions = data["market_cap"] / 1e9 if data["market_cap"] else 0
            if cap_billions < filters["min_market_cap"]:
                continue

        results.append(data)

    return results