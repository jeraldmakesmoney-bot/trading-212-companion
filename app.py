import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Premium app config
st.set_page_config(page_title="iOS 26 Quantum Terminal", layout="wide", initial_sidebar_state="expanded")

# --- iOS 26 High-Fidelity Style Engine ---
THEMES = {
    "📱 iOS 26 Cosmic Dark": {
        "bg_css": """
            body { background: radial-gradient(circle at top right, #0d0d12, #161622); color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 700; font-size: 2.0rem !important; }
        """,
        "card_style": "background: rgba(30, 30, 45, 0.4); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); margin-bottom: 25px;",
        "up_color": "#ff453a",     # Apple Crimson Red
        "down_color": "#30d158",   # Apple Emerald Green
        "ema9": "#0a84ff",         # Apple Electric Blue
        "ema21": "#bf5af2",        # Apple Bright Purple
        "grid": "rgba(255, 255, 255, 0.05)"
    },
    "❄️ iOS 26 Fluid Light": {
        "bg_css": """
            body { background: linear-gradient(135deg, #f5f5f7 0%, #e5e5ea 100%); color: #1d1d1f; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            [data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 700; font-size: 2.0rem !important; }
        """,
        "card_style": "background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(0, 0, 0, 0.05); padding: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05); margin-bottom: 25px;",
        "up_color": "#ff3b30",
        "down_color": "#34c759",
        "ema9": "#007aff",
        "ema21": "#af52de",
        "grid": "rgba(0, 0, 0, 0.05)"
    }
}

# --- Control Panel Setup ---
st.sidebar.header("🕹️ OS Style Controls")
selected_theme = st.sidebar.selectbox("Display Matrix Style:", list(THEMES.keys()))
theme = THEMES[selected_theme]
st.markdown(f"<style>{theme['bg_css']}</style>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.header("🗂️ Asset Routing")
search_mode = st.sidebar.radio("Navigation Target:", ["Browse Preset Library", "Manual System Entry"])

ASSET_LIBRARIES = {
    "🇺🇸 Tech Giants": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"],
    "🌍 Global Indices": ["^GSPC", "^IXIC", "^FTSE", "^GDAXI"],
    "💱 Forex Markets": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
    "🪙 Crypto Markets": ["BTC-USD", "ETH-USD"]
}

if search_mode == "Browse Preset Library":
    library_choice = st.sidebar.selectbox("Focus Asset Class:", list(ASSET_LIBRARIES.keys()))
    tickers = ASSET_LIBRARIES[library_choice]
else:
    custom_input = st.sidebar.text_input("Custom Target Pipelines (comma split):", "AAPL, NVDA")
    tickers = [t.strip().upper() for t in custom_input.split(",")]

st.sidebar.markdown("---")

# --- Feature 1: Apple-Style CFD Risk Calculator Widget ---
st.sidebar.header("🧮 CFD Risk & Sizing Engine")
account_balance = st.sidebar.number_input("Account Balance ($/£):", min_value=10.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Risk Tolerance per Trade (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_loss_distance = st.sidebar.number_input("Stop Loss Distance (Points/Cents):", min_value=0.01, value=1.50, step=0.10)

# Calculate total cash capital at risk
cash_risk = account_balance * (risk_percentage / 100.0)
exact_position_size = cash_risk / stop_loss_distance

st.sidebar.markdown(f"""
<div style="background: rgba(10, 132, 255, 0.1); border-radius: 12px; padding: 12px; border: 1px solid rgba(10, 132, 255, 0.2);">
    <small style="color: gray; display:block;">MAX CASH RISK</small>
    <b style="font-size: 1.1rem;">${cash_risk:.2f}</b>
    <small style="color: gray; display:block; margin-top: 6px;">SUGGESTED CFD POSITION SIZE</small>
    <b style="font-size: 1.1rem; color: #0a84ff;">{exact_position_size:.2f} Units</b>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
primary_interval = st.sidebar.selectbox("Primary Display Chart Interval:", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
primary_period = period_map[primary_interval]

# --- Main Workspace Viewport ---
st.title(" Quantum Multi-Radar Platform")
st.caption(f"Engine Profile: **{selected_theme}** // Refresh State: Active (15s Loop)")
st.markdown("---")

trigger_audio = False
cols = st.columns(len(tickers))

# Function to parse individual matrix math sets
def calculate_tf_signal(ticker_id, tf_interval, tf_period):
    try:
        data = yf.Ticker(ticker_id).history(period=tf_period, interval=tf_interval)
        if data.empty or len(data) < 22:
            return "⏳"
        e9 = data['Close'].ewm(span=9, adjust=False).mean().iloc[-1]
        e21 = data['Close'].ewm(span=21, adjust=False).mean().iloc[-1]
        return "🟢" if e9 > e21 else "🔴"
    except:
        return "❌"

for i, ticker in enumerate(tickers):
    with cols[i]:
        clean_name = ticker.replace("^", "").replace("=X", "")
        
        # Open Glassmorphism Visual Block
        st.markdown(f'<div style="{theme["card_style"]}">', unsafe_allow_html=True)
        st.markdown(f"### {clean_name}")
        
        try:
            # Main Data Pipeline Fetch
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period=primary_period, interval=primary_interval)
            
            if df.empty:
                st.error("Data Vector Offline")
                st.markdown('</div>', unsafe_allow_html=True)
                continue
                
            # Core Analytical Engineering
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
            rsi_val = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # --- Feature 2: Multi-Timeframe Confluence Engine Mapping ---
            sig_5m = calculate_tf_signal(ticker, "5m", "1d") if primary_interval in ["5m"] else "—"
            sig_15m = calculate_tf_signal(ticker, "15m", "5d") if primary_interval in ["5m", "15m"] else "—"
            sig_1h = calculate_tf_signal(ticker, "1h", "1mo")
            sig_1d = calculate_tf_signal(ticker, "1d", "1y")
            
            # Primary strategy triggers
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            rsi_oversold = rsi_val < 35
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            rsi_overbought = rsi_val > 65

            if (ema_buy and macd_buy) or rsi_oversold:
                status_color = "green"
                status_text = "EXECUTE BUY 🟢"
                trigger_audio = True
            elif (ema_sell and macd_sell) or rsi_overbought:
                status_color = "red"
                status_text = "EXECUTE SELL 🔴"
                trigger_audio = True
            else:
                status_color = "orange" if "Light" in selected_theme else "gray"
                status_text = "STABLE HOLD ⏳"
            
            display_price = f"{price:.4f}" if "=X" in ticker else f"${price:,.2f}"
            st.metric(label=f"Primary ({primary_interval}) Close", value=display_price)
            st.markdown(f"**Verdict:** :{status_color}[{status_text}]")
            
            # --- Confluence Render Interface UI ---
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 10px; margin-top: 10px; margin-bottom: 10px; font-size: 0.85rem;">
                <b style="display:block; margin-bottom: 4px; color:gray;">Confluence Matrix:</b>
                ⚡ 5m: {sig_5m} | 🕐 15m: {sig_15m} | 📊 1h: {sig_1h} | 🗺️ 1d: {sig_1d}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**RSI Momentum Index:** `{rsi_val:.1f}`")
            
            # --- Smooth Candlestick Canvas Rendering ---
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Price",
                increasing_line_color=theme['down_color'],  
                decreasing_line_color=theme['up_color']
            ))
            
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', line=dict(color=theme['ema9'], width=2)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', line=dict(color=theme['ema21'], width=2)))
            
            fig.update_layout(
                height=240,
                margin=dict(l=0, r=0, t=5, b=0),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, tickfont=dict(color='gray', size=9)),
                yaxis=dict(showgrid=True, gridcolor=theme['grid'], tickfont=dict(color='gray', size=9))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            st.error("Matrix Sync Error")
            
        # Close Glassmorphism Card Element
        st.markdown('</div>', unsafe_allow_html=True)

# Continuous Audio Beacon Delivery
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
