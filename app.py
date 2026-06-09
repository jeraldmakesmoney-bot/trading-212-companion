import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Initialize terminal workspace on an expansive ultra-wide grid layout
st.set_page_config(page_title="Quantum Terminal // Pro Desk", layout="wide", initial_sidebar_state="expanded")

# --- Apple x Wall Street Hybrid Terminal Stylesheet ---
TERMINAL_CSS = """
<style>
    body {
        background-color: #000000 !important;
        color: #E5E5EA !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", SFMono-Regular, Menlo, sans-serif !important;
    }
    .stApp {
        background-color: #000000 !important;
    }
    /* Bloomberg-Density Apple Glass Cards */
    .terminal-card {
        background: rgba(18, 18, 20, 0.8);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.07);
        padding: 20px;
        margin-bottom: 20px;
    }
    /* Monospaced Ticker Row for Institutional Feel */
    .ticker-pill {
        font-family: "SF Mono", SFMono-Regular, Menlo, monospace;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.04);
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    section[data-testid="stSidebar"] {
        background-color: #0D0D0E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    /* Institutional Metric Layouts */
    div[data-testid="stMetricValue"] {
        font-family: "SF Pro Display", -apple-system, sans-serif !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em !important;
        color: #FFFFFF !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: "SF Mono", monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.06em !important;
        color: #8E8E93 !important;
        text-transform: uppercase;
    }
    /* Clean up the native dataframes to look like a terminal grid */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px;
    }
</style>
"""
st.markdown(TERMINAL_CSS, unsafe_allow_html=True)

# --- Command Controls (Sidebar) ---
st.sidebar.markdown("<h2 style='margin-top:0; letter-spacing:-0.03em;'>SYSTEM COMMAND</h2>", unsafe_allow_html=True)

if st.sidebar.button("📡 RE-SCAN GLOBAL MATRIX", use_container_width=True):
    st.cache_data.clear()

st.sidebar.markdown("---")

# --- Institutional Risk & Sizing Computer ---
st.sidebar.markdown("### 🧮 ALLOCATION COMPUTER")
account_balance = st.sidebar.number_input("Account Equity ($):", min_value=10.0, value=10000.0, step=1000.0)
risk_slider = st.sidebar.slider("Risk Threshold Per Asset (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_points = st.sidebar.number_input("Invalidation Range (Points):", min_value=0.01, value=1.50, step=0.10)
target_multiplier = st.sidebar.slider("Target Yield Multiplier:", min_value=1.0, max_value=5.0, value=2.5, step=0.5)

# Sizing Calculations
capital_at_risk = account_balance * (risk_slider / 100.0)
position_size_units = capital_at_risk / stop_points
target_payout = capital_at_risk * target_multiplier
profit_points_distance = stop_points * target_multiplier

st.sidebar.markdown(f"""
<div style="background: rgba(10, 132, 255, 0.06); border-radius: 10px; padding: 14px; border: 1px solid rgba(10, 132, 255, 0.2); margin-top: 12px;">
    <small style="font-family: 'SF Mono', monospace; color: #8E8E93; display:block; font-size:0.7rem; letter-spacing:0.05em;">TOTAL CAPITAL RISK LIMIT</small>
    <b style="font-size: 1.3rem; color: #FF453A; font-family: 'SF Pro Display';">-${capital_at_risk:.2f}</b><br>
    <small style="font-family: 'SF Mono', monospace; color: #8E8E93; display:block; margin-top: 8px; font-size:0.7rem; letter-spacing:0.05em;">ALGORITHMIC PROFIT TARGET</small>
    <b style="font-size: 1.3rem; color: #30D158; font-family: 'SF Pro Display';">+${target_payout:.2f}</b><br>
    <small style="font-family: 'SF Mono', monospace; color: #8E8E93; display:block; margin-top: 8px; font-size:0.7rem; letter-spacing:0.05em;">DESK POSITION SIZE VALUE</small>
    <b style="font-size: 1.3rem; color: #0A84FF; font-family: 'SF Pro Display';">{position_size_units:.2f} Units</b>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
interval_selection = st.sidebar.selectbox("Desk Pulse Velocity:", ["5m", "15m", "1h", "1d"], index=1)
period_dictionary = {"5m": "5d", "15m": "5d", "1h": "1mo", "1d": "1y"}
selected_period = period_dictionary[interval_selection]

# Watchlist Pipeline Arrays
DESK_WATCHLIST = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AMD", "EURUSD=X", "GBPUSD=X", "BTC-USD"]

# --- High-Velocity Stream Core ---
@st.cache_data(ttl=15)
def pull_terminal_block(tickers, period, interval):
    try:
        return yf.download(tickers=tickers, period=period, interval=interval, group_by='ticker', auto_adjust=True)
    except:
        return pd.DataFrame()

def run_power_calculations(df, period=14):
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

# Instantaneous Master Data Download Frame
terminal_data_package = pull_terminal_block(DESK_WATCHLIST, selected_period, interval_selection)

# --- UNIFIED COMMAND DASHBOARD INTERFACE ---
# Displays everything simultaneously on one dense screen layout, removing tabs completely
st.markdown("<h2 style='margin-bottom:5px; letter-spacing:-0.04em;'> QUANTUM EXECUTIVE COMMAND</h2>", unsafe_allow_html=True)
st.caption(f"Desk Feed Status: Synced // Dynamic Interval Rate: {interval_selection}")
st.markdown("---")

# Top Layout Row: Global Market Grid Frame
st.markdown("<h4 style='font-family: monospace; letter-spacing:0.05em; color:#8E8E93 !important;'>[01] INSTANT RADAR MATRIX</h4>", unsafe_allow_html=True)

matrix_grid_payload = []
if not terminal_data_package.empty:
    for ticker in DESK_WATCHLIST:
        try:
            if ticker not in terminal_data_package.columns.levels[0]:
                continue
            df = terminal_data_package[ticker].dropna(how='all')
            if len(df) < 22:
                continue
            
            df['Fast_Acceleration'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['Trend_Backbone'] = df['Close'].ewm(span=21, adjust=False).mean()
            df['Engine_Power'] = run_power_calculations(df)
            
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                tp = (df['High'] + df['Low'] + df['Close']) / 3
                df['Institutional_Value'] = (tp * df['Volume']).cumsum() / df['Volume'].cumsum()
            else:
                df['Institutional_Value'] = df['Close']

            latest = df.iloc[-1]
            price = latest['Close']
            power_metric = latest['Engine_Power']
            
            bullish_alignment = latest['Fast_Acceleration'] > latest['Trend_Backbone']
            value_supported = price > latest['Institutional_Value']
            
            if power_metric < 20:
                environment_label = "⚠️ Sideways Inactive Chop"
                trade_execution_state = "🔲 HOLD SYSTEM STANDBY"
            else:
                environment_label = "⚡ High Velocity Active Trend"
                if bullish_alignment and value_supported:
                    trade_execution_state = "🟩 EXECUTING ACTIVE BUY"
                elif not bullish_alignment and not value_supported:
                    trade_execution_state = "🟥 EXECUTING ACTIVE SHORT"
                else:
                    trade_execution_state = "🔲 CONSOLIDATION NEUTRAL"
            
            matrix_grid_payload.append({
                "TICKER FEED": ticker,
                "EXECUTION PRICE": f"${price:,.2f}" if "=X" not in ticker else f"{price:.4f}",
                "ENGINE POWER (ADX)": f"{power_metric:.1f}%",
                "MARKET ENVIRONMENT STRUCTURE": environment_label,
                "AUTOMATED DESK STATE": trade_execution_state
            })
        except:
            continue

if matrix_grid_payload:
    st.dataframe(pd.DataFrame(matrix_grid_payload), use_container_width=True, hide_index=True)
else:
    st.error("Matrix link severed. Attempting reconnect protocol...")

st.markdown("---")

# Bottom Layout Row: Split Deep Dive Workspace Engine
st.markdown("<h4 style='font-family: monospace; letter-spacing:0.05em; color:#8E8E93 !important;'>[02] ANALYTICAL STUDIO COMMAND CANVAS</h4>", unsafe_allow_html=True)

workspace_col1, workspace_col2 = st.columns([1, 3])

with workspace_col1:
    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
    focused_ticker_feed = st.selectbox("Focus Asset Core Frame:", DESK_WATCHLIST, label_visibility="collapsed")
    
    # Process isolated focus vector metrics
    if focused_ticker_feed and not terminal_data_package.empty and focused_ticker_feed in terminal_data_package.columns.levels[0]:
        df_focus = terminal_data_package[focused_ticker_feed].dropna(how='all')
        if len(df_focus) >= 22:
            df_focus['Fast_Acceleration'] = df_focus['Close'].ewm(span=9, adjust=False).mean()
            df_focus['Trend_Backbone'] = df_focus['Close'].ewm(span=21, adjust=False).mean()
            df_focus['Engine_Power'] = run_power_calculations(df_focus)
            
            if 'Volume' in df_focus.columns and df_focus['Volume'].sum() > 0:
                tp = (df_focus['High'] + df_focus['Low'] + df_focus['Close']) / 3
                df_focus['Institutional_Value'] = (tp * df_focus['Volume']).cumsum() / df_focus['Volume'].cumsum()
            else:
                df_focus['Institutional_Value'] = df_focus['Close']

            latest_f = df_focus.iloc[-1]
            price_f = float(latest_f['Close'])
            power_f = float(latest_f['Engine_Power'])
            is_bullish_f = latest_f['Fast_Acceleration'] > latest_f['Trend_Backbone']
            
            if is_bullish_f:
                status_header = "ADVANCING BULL MATRIX"
                sl_coordinate = price_f - stop_points
                tp_coordinate = price_f + profit_points_distance
            else:
                status_header = "ACCELERATING BEAR MATRIX"
                sl_coordinate = price_f + stop_points
                tp_coordinate = price_f - profit_points_distance

            # Institutional Terminal Metric Card blocks
            st.markdown(f"""
            <div class="terminal-card" style="margin-top:10px;">
                <small style="font-family:'SF Mono', monospace; color:#8E8E93; font-size:0.75rem;">LIVE EXECUTION QUOTE</small>
                <div style="font-size:2.2rem; font-weight:700; color:#FFFFFF; margin-bottom:15px; letter-spacing:-0.03em;">
                    {"$" if "=X" not in focused_ticker_feed else ""}{price_f:,.4f if "=X" in focused_ticker_feed else ".,2f"}
                </div>
                
                <small style="font-family:'SF Mono', monospace; color:#8E8E93; font-size:0.75rem;">TREND POWER COEFFICIENT</small>
                <div style="font-size:2.2rem; font-weight:700; color:#0A84FF; margin-bottom:15px; letter-spacing:-0.03em;">
                    {power_f:.1f}%
                </div>
                
                <small style="font-family:'SF Mono', monospace; color:#8E8E93; font-size:0.75rem;">DESK DIRECTIONAL MODE</small>
                <div style="font-size:1.1rem; font-weight:600; color:{'#30D158' if is_bullish_f else '#FF453A'}; margin-bottom:5px;">
                    {status_header}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Risk Target HUD Display Blocks
            st.markdown(f"""
            <div class="terminal-card" style="padding:15px; background:rgba(255,255,255,0.02);">
                <div style="margin-bottom:8px;">🎯 <span style="font-family:'SF Mono', monospace; font-size:0.75rem; color:#8E8E93;">PROFIT TARGET (TP):</span> <b style="color:#30D158; font-family:monospace; float:right;">{tp_coordinate:.4f}</b></div>
                <div>🛡️ <span style="font-family:'SF Mono', monospace; font-size:0.75rem; color:#8E8E93;">RISK INVALIDATION (SL):</span> <b style="color:#FF453A; font-family:monospace; float:right;">{sl_coordinate:.4f}</b></div>
            </div>
            """, unsafe_allow_html=True)

with workspace_col2:
    if focused_ticker_feed and 'df_focus' in locals():
        # Clean, inline toggle controllers designed directly into the terminal window header area
        tc1, tc2, tc3 = st.columns(3)
        with tc1: toggle_acceleration = st.checkbox("Overlay Acceleration Lines", value=True)
        with tc2: toggle_institutions = st.checkbox("Overlay Institutional Value Line", value=True)
        with tc3: toggle_brackets = st.checkbox("Overlay Risk Targets Matrix", value=True)
        
        # Build High-Fidelity Reactive Canvas Pipeline
        fig = go.Figure()
        
        # High contrast cyber candlesticks
        fig.add_trace(go.Candlestick(
            x=df_focus.index, open=df_focus['Open'], high=df_focus['High'], low=df_focus['Low'], close=df_focus['Close'],
            increasing_line_color='#30D158', decreasing_line_color='#FF453A',
            increasing_fillcolor='rgba(48, 209, 88, 0.15)', decreasing_fillcolor='rgba(255, 69, 58, 0.15)',
            name="Candlestick Trace"
        ))
        
        if toggle_acceleration:
            fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['Fast_Acceleration'], mode='lines', line=dict(color='#0A84FF', width=1.5), name="Fast Acceleration Line"))
            fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['Trend_Backbone'], mode='lines', line=dict(color='#BF5AF2', width=1.5), name="Trend Backbone Highway"))
            
        if toggle_institutions:
            fig.add_trace(go.Scatter(x=df_focus.index, y=df_focus['Institutional_Value'], mode='lines', line=dict(color='#FF9500', width=1.2, dash='dash'), name="Institutional Value Average"))
            
        if toggle_brackets:
            fig.add_hline(y=tp_coordinate, line_dash="solid", line_color="rgba(48, 209, 88, 0.8)", line_width=1.5, annotation_text="TERMINAL TARGET PROFIT EXIT LEVEL", annotation_font_color="#30D158")
            fig.add_hline(y=sl_coordinate, line_dash="solid", line_color="rgba(255, 69, 58, 0.8)", line_width=1.5, annotation_text="TERMINAL EMERGENCY LIQUIDATION LIMIT", annotation_font_color="#FF453A")

        # Premium Terminal Geometry Configuration Layout
        fig.update_layout(
            height=460,
            margin=dict(l=5, r=5, t=5, b=5),
            xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, color="#8E8E93", font=dict(family="monospace")),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color="#8E8E93", side="right", font=dict(family="monospace")),
            hovermode="x unified", # Parallel multi-line crosshair data tracker
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(family="monospace", size=10))
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
