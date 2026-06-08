import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Premium app config
st.set_page_config(page_title="iOS 26 Quantum Max", layout="wide", initial_sidebar_state="expanded")

# --- iOS 26 High-Fidelity Style Engine ---
THEMES = {
    "📱 iOS 26 Cosmic Dark": {
        "bg_css": "body { background: radial-gradient(circle at top right, #0d0d12, #161622); color: #f5f5f7; font-family: -apple-system, BlinkMacSystemFont, sans-serif; } [data-testid='stMetricValue'] { color: #ffffff !important; font-weight: 700; font-size: 2.0rem !important; }",
        "card_style": "background: rgba(30, 30, 45, 0.4); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.08); padding: 20px; margin-bottom: 25px;",
        "up_color": "#ff453a", "down_color": "#30d158", "ema9": "#0a84ff", "ema21": "#bf5af2", "grid": "rgba(255, 255, 255, 0.05)"
    },
    "❄️ iOS 26 Fluid Light": {
        "bg_css": "body { background: linear-gradient(135deg, #f5f5f7 0%, #e5e5ea 100%); color: #1d1d1f; font-family: -apple-system, BlinkMacSystemFont, sans-serif; } [data-testid='stMetricValue'] { color: #1d1d1f !important; font-weight: 700; font-size: 2.0rem !important; }",
        "card_style": "background: rgba(255, 255, 255, 0.5); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(0, 0, 0, 0.05); padding: 20px; margin-bottom: 25px;",
        "up_color": "#ff3b30", "down_color": "#34c759", "ema9": "#007aff", "ema21": "#af52de", "grid": "rgba(0, 0, 0, 0.05)"
    }
}

st.sidebar.header("🕹️ OS Controls")
selected_theme = st.sidebar.selectbox("Matrix Style:", list(THEMES.keys()))
theme = THEMES[selected_theme]
st.markdown(f"<style>{theme['bg_css']}</style>", unsafe_allow_html=True)

# --- MANUAL REFRESH (Prevents API IP Bans) ---
if st.sidebar.button("🔄 Force Data Sync", use_container_width=True):
    pass # Streamlit natively reruns the whole script when a button is clicked

st.sidebar.markdown("---")
st.sidebar.header("🗂️ Asset Routing")
search_mode = st.sidebar.radio("Navigation:", ["Preset Library", "Manual Entry"])

ASSET_LIBRARIES = {
    "🇺🇸 Tech Giants": ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"],
    "🌍 Global Indices": ["^GSPC", "^IXIC", "^FTSE", "^GDAXI"],
    "💱 Forex Markets": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
    "🪙 Crypto Markets": ["BTC-USD", "ETH-USD"]
}

if search_mode == "Preset Library":
    library_choice = st.sidebar.selectbox("Asset Class:", list(ASSET_LIBRARIES.keys()))
    tickers = ASSET_LIBRARIES[library_choice]
else:
    custom_input = st.sidebar.text_input("Custom Tickers (comma split):", "AAPL, NVDA")
    tickers = [t.strip().upper() for t in custom_input.split(",") if t.strip()]

st.sidebar.markdown("---")
st.sidebar.header("🧮 Advanced Risk Engine")
account_balance = st.sidebar.number_input("Account Balance:", min_value=10.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Risk per Trade (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_loss_distance = st.sidebar.number_input("Stop Distance (Pts):", min_value=0.01, value=1.50, step=0.10)
risk_reward_ratio = st.sidebar.slider("Risk:Reward Ratio:", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

cash_risk = account_balance * (risk_percentage / 100.0)
exact_position_size = cash_risk / stop_loss_distance
projected_profit = cash_risk * risk_reward_ratio
take_profit_distance = stop_loss_distance * risk_reward_ratio

st.sidebar.markdown(f"""
<div style="background: rgba(10, 132, 255, 0.1); border-radius: 12px; padding: 12px; border: 1px solid rgba(10, 132, 255, 0.2);">
    <small style="color: gray; display:block;">MAX RISK (LOSS)</small>
    <b style="font-size: 1.1rem; color: #ff453a;">-${cash_risk:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">TARGET REWARD</small>
    <b style="font-size: 1.1rem; color: #30d158;">+${projected_profit:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">POSITION SIZE</small>
    <b style="font-size: 1.1rem; color: #0a84ff;">{exact_position_size:.2f} Units</b>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
primary_interval = st.sidebar.selectbox("Chart Interval:", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"} # Safer lookback periods
primary_period = period_map[primary_interval]

st.title(" Quantum Multi-Radar Platform")
st.caption(f"Engine Profile: **{selected_theme}** // Standby Mode (Manual Sync Active)")
st.markdown("---")

# Helper function with safety wrappers
@st.cache_data(ttl=60) # Caches data for 60 seconds to prevent API bans
def fetch_safe_data(ticker_id, p, i):
    try:
        data = yf.Ticker(ticker_id).history(period=p, interval=i)
        return data
    except:
        return pd.DataFrame()

def calculate_tf_signal(ticker_id, tf_interval, tf_period):
    data = fetch_safe_data(ticker_id, tf_period, tf_interval)
    if data.empty or len(data) < 22:
        return "⏳"
    e9 = data['Close'].ewm(span=9, adjust=False).mean().iloc[-1]
    e21 = data['Close'].ewm(span=21, adjust=False).mean().iloc[-1]
    return "🟢" if e9 > e21 else "🔴"

cols = st.columns(len(tickers))

for i, ticker in enumerate(tickers):
    with cols[i]:
        clean_name = ticker.replace("^", "").replace("=X", "")
        st.markdown(f'<div style="{theme["card_style"]}">', unsafe_allow_html=True)
        st.markdown(f"### {clean_name}")
        
        # Safe Data Fetching
        df = fetch_safe_data(ticker, primary_period, primary_interval)
        
        # SAFETY CHECK: Does the asset have enough data to do math?
        if df.empty or len(df) < 30:
            st.warning("Insufficient or closed market data.")
            st.markdown('</div>', unsafe_allow_html=True)
            continue
            
        try:
            # Core Math
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
            
            # Safe VWAP
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3
                df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
                latest_vwap = df['VWAP'].iloc[-1]
                vwap_str = f"${latest_vwap:.2f}"
            else:
                df['VWAP'] = df['Close']
                vwap_str = "N/A"

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = float(latest['Close'])
            rsi_val = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # Safe Confluence Check
            sig_1h = calculate_tf_signal(ticker, "1h", "1mo")
            sig_1d = calculate_tf_signal(ticker, "1d", "1y")
            
            # Entry Filters
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            vwap_buy_filter = price > latest['VWAP']
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            vwap_sell_filter = price < latest['VWAP']

            active_trade = False
            sl_level, tp_level = 0.0, 0.0

            if (ema_buy and (macd > macd_sig) and vwap_buy_filter) or (pd.notna(rsi_val) and rsi_val < 35):
                status_color, status_text = "green", "EXECUTE BUY 🟢"
                active_trade = True
                sl_level, tp_level = price - stop_loss_distance, price + take_profit_distance
            elif (ema_sell and (macd < macd_sig) and vwap_sell_filter) or (pd.notna(rsi_val) and rsi_val > 65):
                status_color, status_text = "red", "EXECUTE SELL 🔴"
                active_trade = True
                sl_level, tp_level = price + stop_loss_distance, price - take_profit_distance
            else:
                status_color, status_text = "gray", "MARKET NEUTRAL ⏳"
            
            display_price = f"{price:.4f}" if "=X" in ticker else f"${price:,.2f}"
            st.metric(label=f"Primary Close ({primary_interval})", value=display_price)
            st.markdown(f"**Verdict:** :{status_color}[{status_text}]")
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 10px; margin-top: 10px; margin-bottom: 10px; font-size: 0.82rem;">
                <b style="display:block; margin-bottom: 4px; color:gray;">Macro Confluence:</b>
                📊 1h: {sig_1h} | 🗺️ 1d: {sig_1d}
            </div>
            """, unsafe_allow_html=True)
            
            if active_trade:
                st.markdown(f"🎯 **Target Profit (TP):** `{tp_level:.4f}`")
                st.markdown(f"🛡️ **Stop Loss (SL):** `{sl_level:.4f}`")
            else:
                st.markdown("🎯 **Target Profit (TP):** `Waiting...`")
                st.markdown("🛡️ **Stop Loss (SL):** `Waiting...`")
            
            # Plotly Charting
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Price", increasing_line_color=theme['down_color'], decreasing_line_color=theme['up_color']
            ))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', line=dict(color=theme['ema9'], width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', line=dict(color=theme['ema21'], width=1.5)))
            
            if active_trade:
                fig.add_hline(y=tp_level, line_dash="dash", line_color="#30d158", line_width=2)
                fig.add_hline(y=sl_level, line_dash="dash", line_color="#ff453a", line_width=2)

            fig.update_layout(
                height=240, margin=dict(l=0, r=0, t=5, b=0), xaxis_rangeslider_visible=False, showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['grid'])
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        except Exception as e:
            # This is the crucial fix: It will now tell you exactly what line of math is failing
            st.error(f"Calculation Error: {str(e)}")
            
        st.markdown('</div>', unsafe_allow_html=True)
