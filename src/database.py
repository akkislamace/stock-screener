from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.types import BigInteger
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/stock_data.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class DimStock(Base):
    __tablename__ = "dim_stocks"
    stock_id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, unique=True, nullable=False, index=True)
    company_name = Column(String)
    sector = Column(String)
    industry = Column(String)
    market_cap = Column(Float)
    country = Column(String)

    prices = relationship("FactStockPrice", back_populates="stock")
    indicators = relationship("FactTechnicalIndicator", back_populates="stock")


class DimDate(Base):
    __tablename__ = "dim_dates"
    date_id = Column(Integer, primary_key=True)  # YYYYMMDD
    full_date = Column(Date, nullable=False, unique=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    week_number = Column(Integer, nullable=False)
    month_name = Column(String)
    is_weekend = Column(Boolean)


class FactStockPrice(Base):
    __tablename__ = "fact_stock_prices"
    date_id = Column(Integer, ForeignKey("dim_dates.date_id"), primary_key=True)
    stock_id = Column(Integer, ForeignKey("dim_stocks.stock_id"), primary_key=True)
    ticker = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(BigInteger)

    stock = relationship("DimStock", back_populates="prices")


class FactTechnicalIndicator(Base):
    __tablename__ = "fact_technical_indicators"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_id = Column(Integer, ForeignKey("dim_dates.date_id"))
    stock_id = Column(Integer, ForeignKey("dim_stocks.stock_id"))
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    volume_sma_20 = Column(Float)

    __table_args__ = (UniqueConstraint("date_id", "stock_id"),)
    stock = relationship("DimStock", back_populates="indicators")


def init_db():
    """Create all tables if they don't exist"""
    Base.metadata.create_all(engine)