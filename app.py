import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Premium app config
st.set_page_config(page_title="iOS 26 Quantum Screener Max", layout="wide", initial_sidebar_state="expanded")

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

if st.sidebar.button("🔄 Force Market Scan", use_container_width=True):
    st.cache_data.clear()

st.sidebar.markdown("---")

# --- Advanced Risk Engine Widget ---
st.sidebar.header("🧮 Position Risk Engine")
account_balance = st.sidebar.number_input("Account Balance:", min_value=10.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Risk per Trade (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_loss_distance = st.sidebar.number_input("Stop Distance (Points):", min_value=0.01, value=1.50, step=0.10)
risk_reward_ratio = st.sidebar.slider("Risk:Reward Ratio Target:", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

cash_risk = account_balance * (risk_percentage / 100.0)
exact_position_size = cash_risk / stop_loss_distance
projected_profit = cash_risk * risk_reward_ratio
take_profit_distance = stop_loss_distance * risk_reward_ratio

st.sidebar.markdown(f"""
<div style="background: rgba(10, 132, 255, 0.1); border-radius: 12px; padding: 12px; border: 1px solid rgba(10, 132, 255, 0.2);">
    <small style="color: gray; display:block;">MAX RISK LIMIT</small>
    <b style="font-size: 1.1rem; color: #ff453a;">-${cash_risk:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">TARGET REWARD</small>
    <b style="font-size: 1.1rem; color: #30d158;">+${projected_profit:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">CFD POSITION SIZE</small>
    <b style="font-size: 1.1rem; color: #0a84ff;">{exact_position_size:.2f} Units</b>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
primary_interval = st.sidebar.selectbox("Analysis Interval:", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"}
primary_period = period_map[primary_interval]

# --- Native Math Function: ADX Engine ---
def calculate_adx(df, period=14):
    df = df.copy()
    df['H-L'] = df['High'] - df['Low']
    df['H-Cp'] = (df['High'] - df['Close'].shift(1)).abs()
    df['L-Cp'] = (df['Low'] - df['Close'].shift(1)).abs()
    df['TR'] = df[['H-L', 'H-Cp', 'L-Cp']].max(axis=1)
    
    df['plus_DM'] = df['High'].diff()
    df['minus_DM'] = df['Low'].diff() * -1
    
    df['plus_DM'] = np.where((df['plus_DM'] > df['minus_DM']) & (df['plus_DM'] > 0), df['plus_DM'], 0)
    df['minus_DM'] = np.where((df['minus_DM'] > df['plus_DM']) & (df['minus_DM'] > 0), df['minus_DM'], 0)
    
    df['TR_smooth'] = df['TR'].ewm(alpha=1/period, adjust=False).mean()
    df['plus_DM_smooth'] = df['plus_DM'].ewm(alpha=1/period, adjust=False).mean()
    df['minus_DM_smooth'] = df['minus_DM'].ewm(alpha=1/period, adjust=False).mean()
    
    df['plus_DI'] = 100 * (df['plus_DM_smooth'] / (df['TR_smooth'] + 1e-10))
    df['minus_DI'] = 100 * (df['minus_DM_smooth'] / (df['TR_smooth'] + 1e-10))
    
    df['DX'] = 100 * (df['plus_DI'] - df['minus_DI']).abs() / (df['plus_DI'] + df['minus_DI'] + 1e-10)
    df['ADX'] = df['DX'].ewm(alpha=1/period, adjust=False).mean()
    return df['ADX']

@st.cache_data(ttl=60)
def fetch_safe_data(ticker_id, p, i):
    try:
        return yf.Ticker(ticker_id).history(period=p, interval=i)
    except:
        return pd.DataFrame()

# Master screening list
SCREENER_POOL = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AMD", "EURUSD=X", "GBPUSD=X", "BTC-USD"]

st.title(" Quantum Automated Radar & Screener")
st.caption(f"Engine Profile: **{selected_theme}** // ADX Filter: Active")
st.markdown("---")

# --- UPGRADE 2 & 3: Background Screener Matrix with ADX Regime Control ---
st.subheader("🕵️‍♂️ Real-Time Asset Screening Radar")

screener_results = []

with st.spinner("Scanning core asset library variables..."):
    for ticker in SCREENER_POOL:
        df = fetch_safe_data(ticker, primary_period, primary_interval)
        if df.empty or len(df) < 30:
            continue
            
        # Run Mathematical Pipeline
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['ADX'] = calculate_adx(df)
        
        # VWAP
        if 'Volume' in df.columns and df['Volume'].sum() > 0:
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
        else:
            df['VWAP'] = df['Close']

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = latest['Close']
        adx_val = latest['ADX']
        
        # Raw Signal Conditions
        ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
        ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
        
        # Regime Verification (ADX Filter)
        if adx_val < 25:
            verdict = "⚠️ CHOP ZONE (No Trade)"
            regime = "Sideways / Consolidation"
        else:
            regime = "Strong Trend Active"
            if ema_buy and price > latest['VWAP']:
                verdict = "🟢 EXECUTE BUY"
            elif ema_sell and price < latest['VWAP']:
                verdict = "🔴 EXECUTE SELL"
            else:
                verdict = "⏳ Market Neutral"
                
        screener_results.append({
            "Asset": ticker,
            "Price": f"${price:,.2f}" if "=X" not in ticker else f"{price:.4f}",
            "Trend Strength (ADX)": f"{adx_val:.1f}",
            "Market Regime": regime,
            "System Action": verdict
        })

# Render background scan output matrix
screener_df = pd.DataFrame(screener_results)
st.dataframe(screener_df, use_container_width=True, hide_index=True)

st.markdown("---")

# --- Focus Viewport Selection ---
st.subheader("🔍 Deep-Dive Diagnostic Canvas")
focus_ticker = st.selectbox("Select screened asset to chart and pull risk targets:", SCREENER_POOL)

if focus_ticker:
    df_focus = fetch_safe_data(focus_ticker, primary_period, primary_interval)
    if not df_focus.empty and len(df_focus) >= 30:
        df_focus['EMA_9'] = df_focus['Close'].ewm(span=9, adjust=False).mean()
        df_focus['EMA_21'] = df_focus['Close'].ewm(span=21, adjust=False).mean()
        df_focus['ADX'] = calculate_adx(df_focus)
        
        if 'Volume' in df_focus.columns and df_focus['Volume'].sum() > 0:
            typical_price = (df_focus['High'] + df_focus['Low'] + df_focus['Close']) / 3
            df_focus['VWAP'] = (typical_price * df_focus['Volume']).cumsum() / df_focus['Volume'].cumsum()
        else:
            df_focus['VWAP'] = df_focus['Close']

        latest_f = df_focus.iloc[-1]
        prev_f = df_focus.iloc[-2]
        price_f = float(latest_f['Close'])
        adx_f = float(latest_f['ADX'])
        
        ema_buy_f = prev_f['EMA_9'] <= prev_f['EMA_21'] and latest_f['EMA_9'] > latest_f['EMA_21']
        ema_sell_f = prev_f['EMA_9'] >= prev_f['EMA_21'] and latest_f['EMA_9'] < latest_f['EMA_21']
        
        active_trade = False
        sl_level, tp_level = 0.0, 0.0
        
        # Trigger conditions only valid if ADX trend metric is strong
        if adx_f >= 25:
            if ema_buy_f and price_f > latest_f['VWAP']:
                active_trade = True
                sl_level, tp_level = price_f - stop_loss_distance, price_f + take_profit_distance
            elif ema_sell_f and price_f < latest_f['VWAP']:
                active_trade = True
                sl_level, tp_level = price_f + stop_loss_distance, price_f - take_profit_distance

        # Visual Interface Rendering
        st.markdown(f'<div style="{theme["card_style"]}">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Focus Price", f"${price_f:,.2f}" if "=X" not in focus_ticker else f"{price_f:.4f}")
        with c2:
            st.metric("ADX Power Metric", f"{adx_f:.1f}")
        with c3:
            if adx_f < 25:
                st.error("🔒 SYSTEM LOCKED: CHOP REGIME")
            elif active_trade:
                st.success("🔓 SIGNAL UNLOCKED: ENTRY VALID")
            else:
                st.info("⏳ STANDBY: LOOKING FOR TREND CROSS")

        if active_trade:
            st.markdown(f"🎯 **Target Profit (TP) Level:** `{tp_level:.4f}`")
            st.markdown(f"🛡️ **Stop Loss (SL) Level:** `{sl_level:.4f}`")
        else:
            st.markdown("🎯 **Target Profit (TP):** `Execution rules suspended or no signal active`")
            st.markdown("🛡️ **Stop Loss (SL):** `Execution rules suspended or no signal active`")

        # Plotly Canvas
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_focus.index, open=df_focus['Open'], high=df_focus['High'], low=df_focus['Low'], close=df_focus['Close'],
            increasing_line_color=theme['down_color'], decreasing_line_color=theme['up_color'], name="Price"
        ))
        fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['EMA_9'], mode='lines', line=dict(color=theme['ema9'], width=1.5), name="EMA 9"))
        fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['EMA_21'], mode='lines', line=dict(color=theme['ema21'], width=1.5), name="EMA 21"))
        fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['VWAP'], mode='lines', line=dict(color='orange', width=1, dash='dash'), name="VWAP"))
        
        if active_trade:
            fig.add_hline(y=tp_level, line_dash="dash", line_color="#30d158", line_width=2)
            fig.add_hline(y=sl_level, line_dash="dash", line_color="#ff453a", line_width=2)

        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=5, b=0), xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor=theme['grid'])
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
