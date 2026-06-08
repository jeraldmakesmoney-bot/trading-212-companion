import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Premium app config
st.set_page_config(page_title="Minimal CFD Terminal", layout="wide", initial_sidebar_state="expanded")

# --- UI Theme Color Configurations ---
THEMES = {
    "Graphite Dark (Pro)": {
        "bg_css": "body { background-color: #1c1c1e; color: #f5f5f7; }",
        "up_color": "#ff453a",     # Apple vibrant red
        "down_color": "#30d158",   # Apple vibrant green
        "ema9": "#0a84ff",         # Apple vibrant blue
        "ema21": "#bf5af2",        # Apple vibrant purple
        "grid": "#2c2c2e"
    },
    "Silver Light (Studio)": {
        "bg_css": "body { background-color: #f5f5f7; color: #1d1d1f; }",
        "up_color": "#ff3b30",     # Apple classic red
        "down_color": "#34c759",   # Apple classic green
        "ema9": "#007aff",         # Apple classic blue
        "ema21": "#af52de",        # Apple classic purple
        "grid": "#e5e5ea"
    },
    "Midnight Blue": {
        "bg_css": "body { background-color: #0a192f; color: #f5f5f7; }",
        "up_color": "#ff453a",
        "down_color": "#64ffda",   # Teal contrast
        "ema9": "#38bdf8",
        "ema21": "#f43f5e",
        "grid": "#1e293b"
    }
}

# --- Sidebar Control Panel ---
st.sidebar.header("🎛️ Design & Workspace")
selected_theme = st.sidebar.selectbox("UI Color Palette:", list(THEMES.keys()))
theme = THEMES[selected_theme]

# Inject the chosen theme's background and core typography CSS
st.markdown(f"<style>{theme['bg_css']}</style>", unsafe_allow_html=True)

st.sidebar.markdown("---")
search_mode = st.sidebar.radio("Input Mode:", ["Browse Asset Library", "Manual Search"])

ASSET_LIBRARIES = {
    "🇺🇸 Tech Giants": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"],
    "🌍 Global Indices": ["^GSPC", "^IXIC", "^FTSE", "^GDAXI"],
    "💱 Forex Markets": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
    "🪙 Crypto Markets": ["BTC-USD", "ETH-USD"]
}

if search_mode == "Browse Asset Library":
    library_choice = st.sidebar.selectbox("Category:", list(ASSET_LIBRARIES.keys()))
    tickers = ASSET_LIBRARIES[library_choice]
else:
    custom_input = st.sidebar.text_input("Enter Tickers (comma separated):", "AAPL, TSLA")
    tickers = [t.strip().upper() for t in custom_input.split(",")]

st.sidebar.markdown("---")
interval = st.sidebar.selectbox("Timeframe Window:", ["5m", "15m", "1h", "1d"], index=1)

period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

# Main Dashboard Interface
st.title("🦅 Studio Asset Radar")
st.caption(f"Currently viewing in **{selected_theme}** profile. Auto-refresh loop active.")
st.markdown("---")

trigger_audio = False
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        clean_name = ticker.replace("^", "").replace("=X", "")
        st.markdown(f"### {clean_name}")
        
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                st.error("No Data Available")
                continue
                
            # --- Analysis Mathematics Engine ---
            df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / (loss + 1e-10)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = float(latest['Close'])
            rsi = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # --- Signal Filter Conditions ---
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            rsi_oversold = rsi < 35
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            rsi_overbought = rsi > 65

            if (ema_buy and macd_buy) or rsi_oversold:
                status_color = "green"
                status_text = "BUY OPTION"
                trigger_audio = True
            elif (ema_sell and macd_sell) or rsi_overbought:
                status_color = "red"
                status_text = "SELL OPTION"
                trigger_audio = True
            else:
                status_color = "orange" if "Light" in selected_theme else "gray"
                status_text = "STABLE HOLD"
            
            # Formatted clean text layout
            display_price = f"{price:.4f}" if "=X" in ticker else f"${price:,.2f}"
            st.metric(label="Market Value", value=display_price)
            st.markdown(f"**Action Verdict:** :{status_color}[{status_text}]")
            st.markdown(f"**RSI Factor:** `{rsi:.1f}`")
            
            # --- Custom Designed Plotly Canvas ---
            fig = go.Figure()
            
            # Dynamic candlestick colors matching selected aesthetic theme profile
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Price",
                increasing_line_color=theme['down_color'],  # Match trading platform directions
                decreasing_line_color=theme['up_color']
            ))
            
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', line=dict(color=theme['ema9'], width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', line=dict(color=theme['ema21'], width=1.5)))
            
            fig.update_layout(
                height=300,
                margin=dict(l=5, r=5, t=5, b=5),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, tickfont=dict(color='gray')),
                yaxis=dict(showgrid=True, gridcolor=theme['grid'], tickfont=dict(color='gray'))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            st.error("Data Interrupted")

if trigger_audio:
    st.components.v1.html(
        """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-500.wav" type="audio/wav">
        </audio>
        """,
        height=0
    )

st.write("")
time.sleep(15)
st.rerun()
