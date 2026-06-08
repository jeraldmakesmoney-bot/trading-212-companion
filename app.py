import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Pro CFD Dashboard", layout="wide")
st.title("🦅 Pro Trading 212 CFD Monitor")
st.caption("Live monitoring multiple assets. Auto-refreshes every 15 seconds.")

# 1. Multi-Ticker Watchlist Sidebar
st.sidebar.header("Watchlist Settings")
watchlist_input = st.sidebar.text_input(
    "Enter Tickers (separated by commas):", 
    "AAPL, TSLA, NVDA, EURUSD=X"
)
interval = st.sidebar.selectbox("Timeframe:", ["5m", "15m", "1h", "1d"], index=1)

# Clean up the input string into a Python list
tickers = [t.strip().upper() for t in watchlist_input.split(",")]

period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

# Track if any action-worthy signal triggers to sound the alert
trigger_audio = False

# Layout the grid based on how many tickers are chosen
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        st.subheader(f"📈 {ticker}")
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                st.error("No data")
                continue
                
            # --- Technical Indicators ---
            # EMAs
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD Upgrade
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            # Latest data dataframes
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Extract current values
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # --- Upgraded Trend Rules ---
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            rsi_oversold = rsi < 35
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            rsi_overbought = rsi > 65

            # Execute Signals
            if (ema_buy and macd_buy) or rsi_oversold:
                status = "BUY 🟢"
                trigger_audio = True
            elif (ema_sell and macd_sell) or rsi_overbought:
                status = "SELL 🔴"
                trigger_audio = True
            else:
                status = "HOLD ⏳"
            
            # Display stats cleanly
            st.metric("Price", f"${price:.2f}" if "X" not in ticker else f"{price:.4f}")
            st.write(f"**RSI:** {rsi:.1f}")
            st.write(f"**Verdict:** {status}")
            
            # Micro-chart for space saving in grids
            st.line_chart(df['Close'], height=150)
            
        except Exception as e:
            st.error("Error")

# 2. Audio Alert Upgrade
# If a signal triggers, inject a hidden HTML audio element to play a chime
if trigger_audio:
    st.components.v1.html(
        """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" type="audio/wav">
        </audio>
        """,
        height=0
    )

# Refresh Loop
time.write("") # Blank space holder
time.sleep(15)
st.rerun()
