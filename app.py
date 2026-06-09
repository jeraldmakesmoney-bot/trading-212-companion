import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Initialize an elite, wide-screen Apple ecosystem layout
st.set_page_config(page_title="iOS 26 Quantum Turbo Max", layout="wide", initial_sidebar_state="expanded")

# --- UI Styling Engine ---
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

st.sidebar.header("🕹️ Workspace Configurations")
selected_theme = st.sidebar.selectbox("Display Theme:", list(THEMES.keys()))
theme = THEMES[selected_theme]
st.markdown(f"<style>{theme['bg_css']}</style>", unsafe_allow_html=True)

# Instant Cache Clear Button to force an immediate data sync
if st.sidebar.button("🔄 Force Fresh Market Scan", use_container_width=True):
    st.cache_data.clear()

st.sidebar.markdown("---")

# --- Risk Calculator Panel ---
st.sidebar.header("🧮 Position Sizing Calculator")
account_balance = st.sidebar.number_input("Trading Balance:", min_value=10.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Cash Risk Per Trade (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_loss_distance = st.sidebar.number_input("Stop Loss Size (Points or Cents):", min_value=0.01, value=1.00, step=0.10)
risk_reward_ratio = st.sidebar.slider("Risk to Reward Ratio Target:", min_value=1.0, max_value=5.0, value=2.0, step=0.5)

# Calculate Risk Math
cash_risk = account_balance * (risk_percentage / 100.0)
exact_position_size = cash_risk / stop_loss_distance
projected_profit = cash_risk * risk_reward_ratio
take_profit_distance = stop_loss_distance * risk_reward_ratio

st.sidebar.markdown(f"""
<div style="background: rgba(10, 132, 255, 0.1); border-radius: 12px; padding: 12px; border: 1px solid rgba(10, 132, 255, 0.2);">
    <small style="color: gray; display:block;">MAX TRADING RISK</small>
    <b style="font-size: 1.1rem; color: #ff453a;">-${cash_risk:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">POTENTIAL TARGET PROFIT</small>
    <b style="font-size: 1.1rem; color: #30d158;">+${projected_profit:.2f}</b><br>
    <small style="color: gray; display:block; margin-top: 6px;">SUGGESTED CFD POSITION SIZE</small>
    <b style="font-size: 1.1rem; color: #0a84ff;">{exact_position_size:.2f} Units</b>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
primary_interval = st.sidebar.selectbox("Chart Timeframe:", ["5m", "15m", "1h", "1d"], index=1)
period_map = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"}
primary_period = period_map[primary_interval]

# Target Assets Array
SCREENER_POOL = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AMD", "EURUSD=X", "GBPUSD=X", "BTC-USD"]

# --- High-Velocity Parallel API Engine ---
@st.cache_data(ttl=15)
def fetch_all_market_data(tickers, period, interval):
    try:
        # Bundles all asset downloads into one single parallel network transmission
        return yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', auto_adjust=True)
    except:
        return pd.DataFrame()

# Clean, Optimized Math Pipeline for ADX Calculation
def calculate_adx_clean(df, period=14):
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
    return df['DX'].ewm(alpha=1/period, adjust=False).mean()

# Header Canvas
st.title(" Quantum Unified Signal Engine")
st.caption(f"System State: Operational // Timeframe Target: {primary_interval}")
st.markdown("---")

# Download market data immediately
batch_data = fetch_all_market_data(SCREENER_POOL, primary_period, primary_interval)

# --- WORKSPACE ARCHITECTURE: CLEAN TABS ---
tab_radar, tab_chart = st.tabs(["🦅 Global Market Radar", "🔬 Interactive Chart Deep-Dive"])

# ================= TAB 1: RADAR =================
with tab_radar:
    st.subheader("Asset Pulse Matrix")
    screener_results = []

    if not batch_data.empty:
        for ticker in SCREENER_POOL:
            try:
                if ticker not in batch_data.columns.levels[0]:
                    continue
                df = batch_data[ticker].dropna(how='all')
                if len(df) < 22:
                    continue
                
                # Math Processing
                df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
                df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
                df['ADX'] = calculate_adx_clean(df)
                
                if 'Volume' in df.columns and df['Volume'].sum() > 0:
                    tp = (df['High'] + df['Low'] + df['Close']) / 3
                    df['VWAP'] = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
                else:
                    df['VWAP'] = df['Close']

                latest = df.iloc[-1]
                price = latest['Close']
                adx_val = latest['ADX']
                
                # State Analytics Engine
                is_bullish = latest['EMA_9'] > latest['EMA_21']
                above_vwap = price > latest['VWAP']
                
                if adx_val < 20:
                    structure = "⚠️ Sideways Chop Zone"
                    verdict = "🟡 BULLISH REGIME (Low Vol)" if is_bullish else "🟡 BEARISH REGIME (Low Vol)"
                else:
                    structure = "⚡ Clean Trending Market"
                    if is_bullish and above_vwap:
                        verdict = "🟢 STRONGLY BULLISH"
                    elif not is_bullish and not above_vwap:
                        verdict = "🔴 STRONGLY BEARISH"
                    else:
                        verdict = "⏳ Mixed Consolidation"
                
                screener_results.append({
                    "Market Ticker": ticker,
                    "Current Price": f"${price:,.2f}" if "=X" not in ticker else f"{price:.4f}",
                    "Trend Power (ADX)": f"{adx_val:.1f}",
                    "Market Structure": structure,
                    "Real-Time State": verdict
                })
            except:
                continue

    if screener_results:
        st.dataframe(pd.DataFrame(screener_results), use_container_width=True, hide_index=True)
    else:
        st.warning("Awaiting initial data sync package.")

# ================= TAB 2: INTERACTIVE CHARTS =================
with tab_chart:
    st.subheader("Advanced Analysis Workspace")
    focus_ticker = st.selectbox("Select Asset to Map:", SCREENER_POOL)
    
    if focus_ticker and not batch_data.empty and focus_ticker in batch_data.columns.levels[0]:
        df_focus = batch_data[focus_ticker].dropna(how='all')
        if len(df_focus) >= 22:
            df_focus['EMA_9'] = df_focus['Close'].ewm(span=9, adjust=False).mean()
            df_focus['EMA_21'] = df_focus['Close'].ewm(span=21, adjust=False).mean()
            df_focus['ADX'] = calculate_adx_clean(df_focus)
            
            if 'Volume' in df_focus.columns and df_focus['Volume'].sum() > 0:
                tp = (df_focus['High'] + df_focus['Low'] + df_focus['Close']) / 3
                df_focus['VWAP'] = (tp * df_focus['Volume']).cumsum() / df_focus['Volume'].cumsum()
            else:
                df_focus['VWAP'] = df_focus['Close']

            latest_f = df_focus.iloc[-1]
            price_f = float(latest_f['Close'])
            adx_f = float(latest_f['ADX'])
            
            is_bull_f = latest_f['EMA_9'] > latest_f['EMA_21']
            
            # Risk coordinate mapper
            if is_bull_f:
                direction_label = "🟢 BULLISH STRUCTURE ACTIVE"
                sl_level = price_f - stop_loss_distance
                tp_level = price_f + take_profit_distance
            else:
                direction_label = "🔴 BEARISH STRUCTURE ACTIVE"
                sl_level = price_f + stop_loss_distance
                tp_level = price_f - take_profit_distance

            # Render Asset Profile Card
            st.markdown(f'<div style="{theme["card_style"]}">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Live Execution Quote", f"${price_f:,.2f}" if "=X" not in focus_ticker else f"{price_f:.4f}")
            with c2:
                st.metric("Trend Strength (ADX)", f"{adx_f:.1f}")
            with c3:
                st.metric("Structural Mode", direction_label)
            
            # Live Metrics Readout
            st.markdown(f"🎯 **Automatic Profit Target (TP):** `{tp_level:.4f}` | 🛡️ **Automatic Stop Loss (SL):** `{sl_level:.4f}`")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # --- HYPER-REACTIVE CHART CONTROLS ---
            st.markdown("##### 🛠️ Live Chart Layers")
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                toggle_emas = st.checkbox("Show Moving Averages (9 & 21 EMA)", value=True)
            with cc2:
                toggle_vwap = st.checkbox("Show Institutional Volume Price (VWAP)", value=True)
            with cc3:
                toggle_risk = st.checkbox("Show Target & Stop Lines (TP/SL)", value=True)
            
            # Canvas Construct
            fig = go.Figure()
            
            # Candlesticks Base
            fig.add_trace(go.Candlestick(
                x=df_focus.index, open=df_focus['Open'], high=df_focus['High'], low=df_focus['Low'], close=df_focus['Close'],
                increasing_line_color=theme['down_color'], decreasing_line_color=theme['up_color'], name="Price Candle"
            ))
            
            # Reactive Layer: EMAs
            if toggle_emas:
                fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['EMA_9'], mode='lines', line=dict(color=theme['ema9'], width=1.5), name="9 Period EMA"))
                fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['EMA_21'], mode='lines', line=dict(color=theme['ema21'], width=1.5), name="21 Period EMA"))
            
            # Reactive Layer: VWAP
            if toggle_vwap:
                fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['VWAP'], mode='lines', line=dict(color='orange', width=1.2, dash='dash'), name="VWAP Line"))
            
            # Reactive Layer: Targets
            if toggle_risk:
                fig.add_hline(y=tp_level, line_dash="solid", line_color="#30d158", line_width=1.5, annotation_text="Profit Target")
                fig.add_hline(y=sl_level, line_dash="solid", line_color="#ff453a", line_width=1.5, annotation_text="Risk Boundary")

            # High-Fidelity Reactive UI Configurations
            fig.update_layout(
                height=450,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=theme['grid']),
                hovermode="x unified", # Hyper-reactive crosshair tracking across the time axis
                showlegend=True
            )
            
            # Render chart onto screen with full interactives unlocked
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
