import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Dashboard adjustments for monitor layout
st.set_page_config(page_title="CFD Companion", layout="wide")
st.title("📊 Trading 212 CFD Signal Companion")
st.caption("Auto-refreshes every 15 seconds to monitor technical setups live.")

# Sidebar controls 
st.sidebar.header("Controls")
ticker_input = st.sidebar.text_input("Stock Ticker (e.g., AAPL, TSLA, NVDA):", "AAPL").upper()
interval = st.sidebar.selectbox("Timeframe:", ["5m", "15m", "1h", "1d"], index=1)

period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

if ticker_input:
    try:
        # Fetch clean market data
        ticker_obj = yf.Ticker(ticker_input)
        df = ticker_obj.history(period=period, interval=interval)
        
        if df.empty:
            st.error(f"No data found for '{ticker_input}'.")
        else:
            # Calculate Indicators
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            current_price = float(latest['Close'])
            rsi_val = float(latest['RSI'])
            ema9_now, ema21_now = float(latest['EMA_9']), float(latest['EMA_21'])
            ema9_prev, ema21_prev = float(prev['EMA_9']), float(prev['EMA_21'])
            
            # Simple technical rules
            buy_condition = (ema9_prev <= ema21_prev and ema9_now > ema21_now) or (rsi_val < 30)
            sell_condition = (ema9_prev >= ema21_prev and ema9_now < ema21_now) or (rsi_val > 70)
            
            if buy_condition and not sell_condition:
                signal_text = "BUY 🟢"
                explanation = "Short-term momentum turned upward or asset is oversold."
            elif sell_condition and not buy_condition:
                signal_text = "SELL 🔴"
                explanation = "Short-term momentum turned downward or asset is overbought."
            else:
                signal_text = "HOLD ⏳"
                explanation = "Indicators are resting in neutral territory."
            
            # Display results via text columns
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${current_price:.2f}")
            col2.metric("RSI (14)", f"{rsi_val:.1f}")
            col3.metric("Action Verdict", signal_text)
            
            st.info(f"**Why this signal?** {explanation}")
            
            # Render visual line chart
            st.subheader(f"Price Action ({interval})")
            st.line_chart(df[['Close', 'EMA_9', 'EMA_21']])
            
    except Exception as e:
        st.error(f"Error fetching ticker: {e}")

# Cloud auto-refresh loop
time.sleep(15)
st.rerun()
