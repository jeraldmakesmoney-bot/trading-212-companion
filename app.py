import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Premium page config
st.set_page_config(page_title="Alpha CFD Terminal", layout="wide", initial_sidebar_state="expanded")

# Custom CSS injection for a sleek dark-mode trading desk feel
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2a2e39;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 Alpha CFD Multi-Radar Desk")
st.caption("Live professional monitoring desk. Auto-refreshing every 15 seconds.")

# Sidebar Configuration
st.sidebar.header("🎛️ Control Panel")
watchlist_input = st.sidebar.text_input(
    "Watchlist Tickers (comma separated):", 
    "AAPL, TSLA, NVDA, EURUSD=X"
)
interval = st.sidebar.selectbox("Timeframe Window:", ["5m", "15m", "1h", "1d"], index=1)

tickers = [t.strip().upper() for t in watchlist_input.split(",")]
period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

trigger_audio = False

# Layout columns dynamically based on watchlist size
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        # Wrap each asset inside its own visual block
        st.markdown(f"### 🪙 {ticker}")
        
        try:
            # Fetch market data
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                st.error("No Data Found")
                continue
                
            # --- Technical Math Engine ---
            # EMAs
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # --- Algorithmic Signal Logic ---
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            rsi_oversold = rsi < 35
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            rsi_overbought = rsi > 65

            if (ema_buy and macd_buy) or rsi_oversold:
                status_color = "green"
                status_text = "🟢 STRAT BUY"
                trigger_audio = True
            elif (ema_sell and macd_sell) or rsi_overbought:
                status_color = "red"
                status_text = "🔴 STRAT SELL"
                trigger_audio = True
            else:
                status_color = "gray"
                status_text = "⚪ NEUTRAL HOLD"
            
            # Display Premium Cards
            display_price = f"${price:.2f}" if "X" not in ticker else f"{price:.4f}"
            
            st.metric(label="Last Price", value=display_price)
            st.markdown(f"**Verdict:** :{status_color}[{status_text}]")
            st.markdown(f"**RSI Momentum:** `{rsi:.1f}`")
            
            # --- Professional Plotly Candlestick Chart ---
            fig = go.Figure()
            
            # 1. Add Candlesticks
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name="Price Action",
                increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            ))
            
            # 2. Add EMA Overlays
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9', line=dict(width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21', line=dict(width=1.5)))
            
            # Clean layout adjustments for compact grid views
            fig.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2a2e39')
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            st.error(f"Data Connection Error")

# Hidden HTML element to trigger audio alerts on state switches
if trigger_audio:
    st.components.v1.html(
        """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" type="audio/wav">
        </audio>
        """,
        height=0
    )

# Fixed Loop: Corrected typo from 'time.write' to 'st.write'
st.write("") 
time.sleep(15)
st.rerun()
