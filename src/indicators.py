import pandas as pd
import numpy as np

def calculate_sma(df, column="close", window=20):
    return df[column].rolling(window=window).mean()

def calculate_rsi(df, column="close", window=14):
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, column="close", fast=12, slow=26, signal=9):
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(df, column="close", window=20, num_std=2):
    sma = df[column].rolling(window=window).mean()
    std = df[column].rolling(window=window).std()
    upper = sma + (std * num_std)
    lower = sma - (std * num_std)
    return upper, sma, lower

def add_all_indicators(df):
    """Add all technical indicators to the dataframe"""
    df = df.copy()
    df["sma_20"] = calculate_sma(df, "close", 20)
    df["sma_50"] = calculate_sma(df, "close", 50)
    df["rsi"] = calculate_rsi(df, "close", 14)
    df["bb_upper"], df["bb_middle"], df["bb_lower"] = calculate_bollinger_bands(df, "close", 20, 2)
    df["volume_sma_20"] = df["volume"].rolling(window=20).mean()
    macd_line, signal_line, histogram = calculate_macd(df, "close")
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_histogram"] = histogram
    return df