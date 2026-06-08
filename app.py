import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Premium page configuration for expanded workspace
st.set_page_config(page_title="Global Asset Radar", layout="wide", initial_sidebar_state="expanded")

# Inject dark theme container styling
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

st.title("🦅 Global CFD Asset Terminal")
st.caption("Live asset tracking desk with built-in macro libraries. Auto-refreshes every 15 seconds.")

# --- Built-In Asset Library Definitions ---
ASSET_LIBRARIES = {
    "🇺🇸 US Tech Giants": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL"],
    "🌍 Major Indices": ["^GSPC", "^IXIC", "^DJI", "^FTSE", "^GDAXI"],
    "💱 Forex CFDs": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"],
    "🪙 Crypto CFDs": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

# --- Sidebar Controls ---
st.sidebar.header("🗂️ Asset Library")

# Mode selection: Use built-in libraries OR custom manual input
search_mode = st.sidebar.radio("Select Input Mode:", ["Browse Library Grid", "Manual Custom Ticker"])

if search_mode == "Browse Library Grid":
    library_choice = st.sidebar.selectbox("Choose Asset Category:", list(ASSET_LIBRARIES.keys()))
    tickers = ASSET_LIBRARIES[library_choice]
    st.sidebar.info(f"Monitoring: {', '.join(tickers)}")
else:
    custom_input = st.sidebar.text_input("Enter Custom Tickers (comma separated):", "AAPL, TSLA")
    tickers = [t.strip().upper() for t in custom_input.split(",")]

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Strategy Settings")
interval = st.sidebar.selectbox("Timeframe Window:", ["5m", "15m", "1h", "1d"], index=1)

period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

trigger_audio = False

# Layout columns dynamically based on selected library size
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        # Visual title adjustments for indices vs standard stocks
        clean_name = ticker.replace("^", "").replace("=X", "")
        st.markdown(f"### 📊 {clean_name}")
        
        try:
            # Fetch market data safely
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                st.error("No Data")
                continue
                
            # --- Technical Analysis Engine ---
            # Exponential Moving Averages
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            # Relative Strength Index
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
            
            # --- Technical Crossover Strategies ---
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
            
            # Render visual data blocks
            if "=X" in ticker:
                display_price = f"{price:.4f}"
            elif price > 1000:
                display_price = f"${price:,.2f}"
            else:
                display_price = f"${price:.2f}"
                
            st.metric(label="Last Price", value=display_price)
            st.markdown(f"**Verdict:** :{status_color}[{status_text}]")
            st.markdown(f"**RSI Value:** `{rsi:.1f}`")
            
            # --- Interactive Candlestick Integration ---
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Candles", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
            ))
            
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9', line=dict(width=1.2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21', line=dict(width=1.2)))
            
            fig.update_layout(
                height=280,
                margin=dict(l=5, r=5, t=5, b=5),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#2a2e39')
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            st.error("Connection Error")

# Handle system audio notifications if active thresholds cross
if trigger_audio:
    st.components.v1.html(
        """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" type="audio/wav">
        </audio>
        """,
        height=0
    )

# Refresh framework
st.write("") 
time.sleep(15)
st.rerun()
