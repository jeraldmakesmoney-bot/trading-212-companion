import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# Premium app config
st.set_page_config(page_title="iOS 26 CFD Terminal", layout="wide", initial_sidebar_state="expanded")

# --- iOS 26 Futuristic Theme Configuration ---
THEMES = {
    "📱 iOS 26 Cosmic Dark": {
        "bg_css": """
            body { background: radial-gradient(circle at top right, #0d0d12, #161622); color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 700; font-size: 2.2rem !important; }
        """,
        "card_style": "background: rgba(30, 30, 45, 0.4); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);",
        "up_color": "#ff453a",     # Apple Crimson Red
        "down_color": "#30d158",   # Apple Emerald Green
        "ema9": "#0a84ff",         # Apple Electric Blue
        "ema21": "#bf5af2",        # Apple Bright Purple
        "grid": "rgba(255, 255, 255, 0.05)"
    },
    "❄️ iOS 26 Fluid Light": {
        "bg_css": """
            body { background: linear-gradient(135deg, #f5f5f7 0%, #e5e5ea 100%); color: #1d1d1f; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            [data-testid="stMetricValue"] { color: #1d1d1f !important; font-weight: 700; font-size: 2.2rem !important; }
        """,
        "card_style": "background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(0, 0, 0, 0.05); padding: 20px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);",
        "up_color": "#ff3b30",     # Deep Red
        "down_color": "#34c759",   # Deep Green
        "ema9": "#007aff",         # Royal Blue
        "ema21": "#af52de",        # Royal Purple
        "grid": "rgba(0, 0, 0, 0.05)"
    },
    "🔮 iOS 26 Cyber Neon": {
        "bg_css": """
            body { background: #05050a; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
            [data-testid="stMetricValue"] { color: #64ffda !important; font-weight: 800; font-size: 2.2rem !important; }
        """,
        "card_style": "background: rgba(10, 10, 25, 0.6); border-radius: 20px; border: 1px solid #64ffda; padding: 20px; box-shadow: 0 0 15px rgba(100, 255, 218, 0.15);",
        "up_color": "#ff2a5f",     # Cyber Pink
        "down_color": "#00f5d4",   # Neon Teal
        "ema9": "#00bbf9",         # Neon Cyan
        "ema21": "#9b5de5",        # Neon Purple
        "grid": "rgba(100, 255, 218, 0.05)"
    }
}

# --- Sidebar Controls ---
st.sidebar.header("🕹️ UI Core Engine")
selected_theme = st.sidebar.selectbox("iOS 26 Style Matrix:", list(THEMES.keys()))
theme = THEMES[selected_theme]

# Inject Global Styling Framework
st.markdown(f"<style>{theme['bg_css']}</style>", unsafe_allow_html=True)

st.sidebar.markdown("---")
search_mode = st.sidebar.radio("Navigation Mode:", ["Explore Dashboard Grid", "Manual Ticker Core"])

ASSET_LIBRARIES = {
    "🇺🇸 Tech Giants": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"],
    "🌍 Global Indices": ["^GSPC", "^IXIC", "^FTSE", "^GDAXI"],
    "💱 Forex Markets": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
    "🪙 Crypto Markets": ["BTC-USD", "ETH-USD"]
}

if search_mode == "Explore Dashboard Grid":
    library_choice = st.sidebar.selectbox("Focus Asset Class:", list(ASSET_LIBRARIES.keys()))
    tickers = ASSET_LIBRARIES[library_choice]
else:
    custom_input = st.sidebar.text_input("Custom Pipeline (comma separated):", "AAPL, NVDA")
    tickers = [t.strip().upper() for t in custom_input.split(",")]

st.sidebar.markdown("---")
interval = st.sidebar.selectbox("Timeframe Frequency:", ["5m", "15m", "1h", "1d"], index=1)

period_map = {"5m": "1d", "15m": "5d", "1h": "1mo", "1d": "1y"}
period = period_map[interval]

# Main Monitor Viewport
st.title(" Quantum Signal Desk")
st.caption(f"OS Status: Active // Engine Profile: **{selected_theme}** // Refresh Rate: 15s")
st.markdown("---")

trigger_audio = False
cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        clean_name = ticker.replace("^", "").replace("=X", "")
        
        # Core Card Glassmorphism Wrapper Open
        st.markdown(f'<div style="{theme["card_style"]}">', unsafe_allow_html=True)
        st.markdown(f"### {clean_name}")
        
        try:
            df = yf.Ticker(ticker).history(period=period, interval=interval)
            if df.empty:
                st.error("Matrix Disconnected")
                st.markdown('</div>', unsafe_allow_html=True)
                continue
                
            # --- Computational Logic Engine ---
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
            
            # --- Indicator Analysis Verification ---
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            rsi_oversold = rsi < 35
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            rsi_overbought = rsi > 65

            if (ema_buy and macd_buy) or rsi_oversold:
                status_color = "green"
                status_text = "EXECUTE BUY"
                trigger_audio = True
            elif (ema_sell and macd_sell) or rsi_overbought:
                status_color = "red"
                status_text = "EXECUTE SELL"
                trigger_audio = True
            else:
                status_color = "orange" if "Light" in selected_theme else "gray"
                status_text = "MARKET NEUTRAL"
            
            display_price = f"{price:.4f}" if "=X" in ticker else f"${price:,.2f}"
            st.metric(label="Current Value", value=display_price)
            st.markdown(f"**System Recommendation:** :{status_color}[{status_text}]")
            st.markdown(f"**RSI Vector:** `{rsi:.1f}`")
            
            # --- Premium Smooth Candlestick Canvas ---
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
                height=260,
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, tickfont=dict(color='gray', size=10)),
                yaxis=dict(showgrid=True, gridcolor=theme['grid'], tickfont=dict(color='gray', size=10))
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            st.error("Pipeline Failure")
            
        # Core Card Wrapper Close
        st.markdown('</div>', unsafe_allow_html=True)

# Audio trigger injection layer
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
