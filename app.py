import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# Premium app config
st.set_page_config(page_title="iOS 26 Quantum Pro", layout="wide", initial_sidebar_state="expanded")

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

# --- CFD Risk & Sizing Engine Widget ---
st.sidebar.header("🧮 CFD Risk & Sizing Engine")
account_balance = st.sidebar.number_input("Account Balance ($/£):", min_value=10.0, value=1000.0, step=100.0)
risk_percentage = st.sidebar.slider("Risk Tolerance per Trade (%):", min_value=0.25, max_value=5.0, value=1.0, step=0.25)
stop_loss_distance = st.sidebar.number_input("Stop Loss Distance (Points/Cents):", min_value=0.01, value=1.50, step=0.10)

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

# Helper function for Timeframe Confluence Matrix
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
                
            # Core Indicators Math
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
            
            # --- UPGRADE 1: Native VWAP (Volume Weighted Average Price) Math ---
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                typical_price = (df['High'] + df['Low'] + df['Close']) / 3
                df['VWAP'] = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
                latest_vwap = df['VWAP'].iloc[-1]
                vwap_str = f"${latest_vwap:.2f}" if "=X" not in ticker else "N/A"
            else:
                df['VWAP'] = df['Close'] # Fallback
                vwap_str = "N/A (No Vol)"

            # --- UPGRADE 2: Native ATR (Average True Range) Trailing Stop Math ---
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift()).abs()
            low_cp = (df['Low'] - df['Close'].shift()).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['ATR'] = tr.ewm(span=14, adjust=False).mean()
            
            latest_atr = df['ATR'].iloc[-1]
            latest_close = df['Close'].iloc[-1]
            # 2x ATR is standard trailing cushion for stops
            suggested_stop_distance = latest_atr * 2.0 
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            price = float(latest['Close'])
            rsi_val = float(latest['RSI'])
            macd, macd_sig = float(latest['MACD']), float(latest['Signal_Line'])
            
            # Multi-Timeframe Confluence Fetching
            sig_5m = calculate_tf_signal(ticker, "5m", "1d") if primary_interval in ["5m"] else "—"
            sig_15m = calculate_tf_signal(ticker, "15m", "5d") if primary_interval in ["5m", "15m"] else "—"
            sig_1h = calculate_tf_signal(ticker, "1h", "1mo")
            sig_1d = calculate_tf_signal(ticker, "1d", "1y")
            
            # Strategy execution rules (Now incorporating VWAP filters)
            ema_buy = prev['EMA_9'] <= prev['EMA_21'] and latest['EMA_9'] > latest['EMA_21']
            macd_buy = macd > macd_sig
            vwap_buy_filter = price > latest['VWAP'] # Only buy if price is above VWAP institutional average
            
            ema_sell = prev['EMA_9'] >= prev['EMA_21'] and latest['EMA_9'] < latest['EMA_21']
            macd_sell = macd < macd_sig
            vwap_sell_filter = price < latest['VWAP']

            if (ema_buy and macd_buy and vwap_buy_filter) or rsi_val < 35:
                status_color = "green"
                status_text = "EXECUTE BUY 🟢"
                trigger_audio = True
                stop_loss_price = price - suggested_stop_distance
            elif (ema_sell and macd_sell and vwap_sell_filter) or rsi_val > 65:
                status_color = "red"
                status_text = "EXECUTE SELL 🔴"
                trigger_audio = True
                stop_loss_price = price + suggested_stop_distance
            else:
                status_color = "orange" if "Light" in selected_theme else "gray"
                status_text = "MARKET NEUTRAL ⏳"
                stop_loss_price = 0.0
            
            display_price = f"{price:.4f}" if "=X" in ticker else f"${price:,.2f}"
            st.metric(label=f"Primary Close ({primary_interval})", value=display_price)
            st.markdown(f"**Verdict:** :{status_color}[{status_text}]")
            
            # Confluence Matrix Render UI
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 10px; margin-top: 10px; margin-bottom: 10px; font-size: 0.82rem;">
                <b style="display:block; margin-bottom: 4px; color:gray;">Confluence Matrix:</b>
                ⚡ 5m: {sig_5m} | 🕐 15m: {sig_15m} | 📊 1h: {sig_1h} | 🗺️ 1d: {sig_1d}
            </div>
            """, unsafe_allow_html=True)
            
            # Protective Volatility Data Card
            stop_display = f"${stop_loss_price:.2f}" if stop_loss_price > 0 else "No Active Trade"
            st.markdown(f"**ATR Smart Stop Price:** `{stop_display}`")
            st.markdown(f"**VWAP Level:** `{vwap_str}`")
            
            # --- Smooth Candlestick Canvas Rendering ---
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="Price", increasing_line_color=theme['down_color'], decreasing_line_color=theme['up_color']
            ))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], mode='lines', name='EMA 9', line=dict(color=theme['ema9'], width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], mode='lines', name='EMA 21', line=dict(color=theme['ema21'], width=1.5)))
            
            # Only graph VWAP if volume data exists
            if 'Volume' in df.columns and df['Volume'].sum() > 0:
                fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines', name='VWAP', line=dict(color='orange', width=1, dash='dash')))
            
            fig.update_layout(
                height=220, margin=dict(l=0, r=0, t=5, b=0), xaxis_rangeslider_visible=False, showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, tickfont=dict(color='gray', size=9)),
                yaxis=dict(showgrid=True, gridcolor=theme['grid'], tickfont=dict(color='gray', size=9))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # --- UPGRADE 3: Native Historical Backtesting Algorithm Matrix ---
            st.markdown("---")
            if st.button(f"📊 Run Backtest Strategy on {clean_name}", key=f"bt_{ticker}"):
                with st.spinner("Processing historical backtest data..."):
                    # Pull a larger 1-year historic block to run simulations
                    bt_df = ticker_obj.history(period="1y", interval="1d")
                    if len(bt_df) > 30:
                        bt_df['EMA_9'] = bt_df['Close'].ewm(span=9, adjust=False).mean()
                        bt_df['EMA_21'] = bt_df['Close'].ewm(span=21, adjust=False).mean()
                        
                        # Generate simple historic signal map
                        bt_df['Signal'] = np.where(bt_df['EMA_9'] > bt_df['EMA_21'], 1, 0)
                        bt_df['Position'] = bt_df['Signal'].diff()
                        
                        # Calculate results
                        trades = []
                        entry_price = 0
                        for idx, row in bt_df.iterrows():
                            if row['Position'] == 1: # Buy Entry
                                entry_price = row['Close']
                            elif row['Position'] == -1 and entry_price != 0: # Sell Close
                                exit_price = row['Close']
                                pnl = (exit_price - entry_price) / entry_price
                                trades.append(pnl)
                                entry_price = 0
                        
                        if len(trades) > 0:
                            win_rate = (len([t for t in trades if t > 0]) / len(trades)) * 100
                            total_return = sum(trades) * 100
                            st.success(f"**1-Year Backtest Results:**")
                            st.markdown(f"📈 Total Returns: `{total_return:.1f}%`")
                            st.markdown(f"🎯 Win Rate: `{win_rate:.1f}%` ({len(trades)} trades)")
                        else:
                            st.info("No definitive strategy crossings in historical period range.")
                    else:
                        st.error("Insufficient historical bar data to compile backtest matrices.")
                        
        except Exception as e:
            st.error("Matrix Sync Error")
            
        # Close Glassmorphism Card Element
        st.markdown('</div>', unsafe_allow_html=True)

# Audio layer engine trigger
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
