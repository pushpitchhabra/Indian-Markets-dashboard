"""
Pre-Market Advanced Technical Analysis Dashboard
==============================================
Enhanced Streamlit interface for comprehensive pre-market technical analysis featuring:
- OHLCV data display
- Multi-timeframe RSI and ADX indicators
- Automated buy/sell/hold recommendations with explanations
- TradingView integration links
- Advanced technical indicators (MACD, Bollinger Bands, Support/Resistance)

Author: AI Assistant for Indian Stock Market Pre-Market Analysis
Created: 2025-01-27
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Import our technical analysis engine
from premarket_technical_analysis_engine import analyze_stock_for_premarket, PreMarketTechnicalAnalysisEngine
from premarket_high_volume_analyzer import PreMarketHighVolumeAnalyzer
from premarket_config import PreMarketConfig, PREMARKET_DISPLAY_CONFIG

def display_technical_analysis_dashboard(kite=None):
    """
    Main function to display the enhanced pre-market technical analysis dashboard.
    """
    st.header("🔬 Advanced Pre-Market Technical Analysis")
    st.markdown("*Comprehensive technical analysis with automated trading recommendations*")
    
    # Initialize analyzers
    premarket_analyzer = PreMarketHighVolumeAnalyzer(kite)
    tech_engine = PreMarketTechnicalAnalysisEngine(kite)
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("⚙️ Analysis Settings")
        
        # Date selection
        analysis_date = st.date_input(
            "Analysis Date",
            value=premarket_analyzer.get_last_trading_day(),
            max_value=date.today()
        )
        
        # Stock selection method
        stock_selection = st.radio(
            "Stock Selection",
            ["High Volume Stocks", "Custom Stock List", "Single Stock Analysis"]
        )
        
        if stock_selection == "Custom Stock List":
            custom_stocks = st.text_area(
                "Enter stock symbols (comma-separated)",
                placeholder="RELIANCE, TCS, INFY, HDFCBANK",
                help="Enter NSE stock symbols separated by commas"
            )
        elif stock_selection == "Single Stock Analysis":
            single_stock = st.text_input(
                "Enter stock symbol",
                placeholder="RELIANCE",
                help="Enter NSE stock symbol"
            )
        
        st.subheader("⚙️ Analysis Options")
        show_ohlcv = st.checkbox("Show OHLCV Data", value=True)
        show_indicators = st.checkbox("Show Technical Indicators", value=True)
        show_decisions = st.checkbox("Show Trading Decisions", value=True)
        show_charts = st.checkbox("Show Interactive Charts", value=False)
        
        st.subheader("📊 Relative Strength Settings")
        benchmark_options = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK", 
            "Nifty IT": "^CNXIT",
            "Nifty Auto": "^CNXAUTO",
            "Nifty Pharma": "^CNXPHARMA"
        }
        selected_benchmark = st.selectbox(
            "Benchmark Index",
            options=list(benchmark_options.keys()),
            index=0,
            help="Select benchmark for relative strength calculation"
        )
        benchmark_symbol = benchmark_options[selected_benchmark]
        
        rs_period = st.number_input(
            "Relative Strength Period (days)",
            min_value=10,
            max_value=252,
            value=55,
            step=5,
            help="Number of days for relative strength calculation"
        )
        
        # Refresh button
        if st.button("🔄 Refresh Analysis", type="primary"):
            st.rerun()
    
    # Main content area
    if stock_selection == "Single Stock Analysis" and 'single_stock' in locals() and single_stock:
        # Single stock detailed analysis
        display_single_stock_analysis(single_stock.upper(), tech_engine, show_ohlcv, show_indicators, show_decisions, show_charts, benchmark_symbol, rs_period)
    
    elif stock_selection == "Custom Stock List" and 'custom_stocks' in locals() and custom_stocks:
        # Custom stock list analysis
        stock_list = [s.strip().upper() for s in custom_stocks.split(',') if s.strip()]
        display_multi_stock_analysis(stock_list, tech_engine, show_ohlcv, show_indicators, show_decisions, benchmark_symbol, rs_period)
    
    else:
        # High volume stocks analysis (default)
        display_high_volume_technical_analysis(premarket_analyzer, tech_engine, analysis_date, show_ohlcv, show_indicators, show_decisions, benchmark_symbol, rs_period)

def display_single_stock_analysis(symbol: str, tech_engine: PreMarketTechnicalAnalysisEngine, 
                                show_ohlcv: bool, show_indicators: bool, show_decisions: bool, show_charts: bool,
                                benchmark_symbol: str = "^NSEI", rs_period: int = 55):
    """Display detailed technical analysis for a single stock."""
    
    st.subheader(f"📈 Detailed Analysis: {symbol}")
    
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            # Get comprehensive analysis
            analysis_result = analyze_stock_for_premarket(symbol, tech_engine.kite, benchmark_symbol, rs_period)
            
            if 'error' in analysis_result:
                st.error(f"Error analyzing {symbol}: {analysis_result['error']}")
                return
            
            # Display TradingView link
            st.markdown(f"**📊 [View on TradingView]({analysis_result['tradingview_link']})**")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Indicators", "🎯 Decision", "📉 Charts"])
            
            with tab1:
                display_stock_overview(analysis_result, show_ohlcv)
            
            with tab2:
                if show_indicators:
                    display_technical_indicators(analysis_result)
            
            with tab3:
                if show_decisions:
                    display_trading_decision(analysis_result)
            
            with tab4:
                if show_charts:
                    display_price_charts(symbol, tech_engine)
                    
        except Exception as e:
            st.error(f"Error analyzing {symbol}: {str(e)}")

def display_multi_stock_analysis(stock_list: List[str], tech_engine: PreMarketTechnicalAnalysisEngine,
                                show_ohlcv: bool, show_indicators: bool, show_decisions: bool,
                                benchmark_symbol: str = "^NSEI", rs_period: int = 55):
    """Display technical analysis for multiple stocks."""
    
    st.subheader(f"📊 Multi-Stock Analysis ({len(stock_list)} stocks)")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    for i, symbol in enumerate(stock_list):
        status_text.text(f"Analyzing {symbol}... ({i+1}/{len(stock_list)})")
        progress_bar.progress((i + 1) / len(stock_list))
        
        try:
            analysis_result = analyze_stock_for_premarket(symbol, tech_engine.kite, benchmark_symbol, rs_period)
            results.append(analysis_result)
        except Exception as e:
            st.warning(f"Error analyzing {symbol}: {str(e)}")
    
    status_text.text("Analysis complete!")
    progress_bar.empty()
    
    # Display results
    display_analysis_summary_table(results, show_ohlcv, show_indicators, show_decisions)

def display_high_volume_technical_analysis(premarket_analyzer: PreMarketHighVolumeAnalyzer, 
                                         tech_engine: PreMarketTechnicalAnalysisEngine,
                                         analysis_date: date, show_ohlcv: bool, 
                                         show_indicators: bool, show_decisions: bool,
                                         benchmark_symbol: str = "^NSEI", rs_period: int = 55):
    """Display technical analysis for high volume stocks."""
    
    st.subheader("🔥 High Volume Stocks - Technical Analysis")
    
    with st.spinner("Fetching high volume stocks and analyzing..."):
        try:
            # Get high volume stocks
            high_volume_data = premarket_analyzer.get_premarket_high_volume_stocks(analysis_date)
            
            if high_volume_data.empty:
                st.warning("No high volume stocks found for the selected date.")
                return
            
            # Get top 10 stocks for detailed analysis
            top_stocks = high_volume_data.head(10)['symbol'].tolist()
            
            st.info(f"Analyzing top {len(top_stocks)} high volume stocks from {analysis_date}")
            
            # Analyze each stock
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, symbol in enumerate(top_stocks):
                status_text.text(f"Analyzing {symbol}... ({i+1}/{len(top_stocks)})")
                progress_bar.progress((i + 1) / len(top_stocks))
                
                try:
                    analysis_result = analyze_stock_for_premarket(symbol, tech_engine.kite, benchmark_symbol, rs_period)
                    results.append(analysis_result)
                except Exception as e:
                    st.warning(f"Error analyzing {symbol}: {str(e)}")
            
            status_text.text("Analysis complete!")
            progress_bar.empty()
            
            # Display results
            display_analysis_summary_table(results, show_ohlcv, show_indicators, show_decisions)
            
        except Exception as e:
            st.error(f"Error in high volume analysis: {str(e)}")

def display_stock_overview(analysis_result: Dict, show_ohlcv: bool):
    """Display stock overview with OHLCV data."""
    
    symbol = analysis_result['symbol']
    analysis = analysis_result['analysis']
    summary = analysis_result['summary']
    
    # Display summary
    st.markdown(f"**📋 Summary:** {summary.get('summary', 'No summary available')}")
    
    if show_ohlcv and 'daily' in analysis['timeframes']:
        daily_data = analysis['timeframes']['daily']
        
        if 'ohlcv' in daily_data:
            ohlcv = daily_data['ohlcv']
            
            # Create OHLCV display
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Open", f"₹{ohlcv['open']}")
            with col2:
                st.metric("High", f"₹{ohlcv['high']}")
            with col3:
                st.metric("Low", f"₹{ohlcv['low']}")
            with col4:
                st.metric("Close", f"₹{ohlcv['close']}")
            with col5:
                volume_formatted = format_volume(ohlcv['volume'])
                st.metric("Volume", volume_formatted)

def display_technical_indicators(analysis_result: Dict):
    """Display technical indicators across timeframes."""
    
    analysis = analysis_result['analysis']
    
    # Create indicator comparison table
    indicator_data = []
    
    timeframes = ['daily', '30min', '15min', '5min']
    
    for tf in timeframes:
        if tf in analysis['timeframes'] and 'indicators' in analysis['timeframes'][tf]:
            indicators = analysis['timeframes'][tf]['indicators']
            
            row = {
                'Timeframe': tf.upper(),
                'RSI': f"{indicators.get('rsi', 'N/A'):.1f}" if not pd.isna(indicators.get('rsi', np.nan)) else 'N/A',
                'ADX': f"{indicators.get('adx', 'N/A'):.1f}" if not pd.isna(indicators.get('adx', np.nan)) else 'N/A'
            }
            
            # Add MACD for daily
            if tf == 'daily':
                macd = indicators.get('macd', {})
                if macd.get('macd') is not None:
                    row['MACD'] = f"{macd['macd']:.4f}"
                    row['Signal'] = f"{macd['signal']:.4f}"
                else:
                    row['MACD'] = 'N/A'
                    row['Signal'] = 'N/A'
            
            indicator_data.append(row)
    
    if indicator_data:
        df_indicators = pd.DataFrame(indicator_data)
        st.dataframe(df_indicators, use_container_width=True)
        
        # Display Bollinger Bands and Support/Resistance for daily
        if 'daily' in analysis['timeframes']:
            daily_indicators = analysis['timeframes']['daily']['indicators']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Bollinger Bands")
                bb = daily_indicators.get('bollinger_bands', {})
                if bb.get('upper') is not None:
                    st.write(f"**Upper Band:** ₹{bb['upper']:.2f}")
                    st.write(f"**Middle Band:** ₹{bb['middle']:.2f}")
                    st.write(f"**Lower Band:** ₹{bb['lower']:.2f}")
                    st.write(f"**Position:** {bb['position']:.1f}%")
                else:
                    st.write("No Bollinger Bands data available")
            
            with col2:
                st.subheader("🎯 Support & Resistance")
                sr = daily_indicators.get('support_resistance', {})
                if sr.get('support') is not None:
                    st.write(f"**Resistance:** ₹{sr['resistance']:.2f}")
                    st.write(f"**Support:** ₹{sr['support']:.2f}")
                else:
                    st.write("No Support/Resistance data available")

def display_trading_decision(analysis_result: Dict):
    """Display automated trading decision with explanation."""
    
    decision_data = analysis_result['decision']
    
    # Decision display with color coding
    decision = decision_data['decision']
    confidence = decision_data['confidence']
    reason = decision_data['reason']
    score = decision_data.get('score', 0)
    
    # Color coding
    if decision == 'BUY':
        decision_color = '🟢'
        bg_color = '#d4edda'
    elif decision == 'SELL':
        decision_color = '🔴'
        bg_color = '#f8d7da'
    else:
        decision_color = '🟡'
        bg_color = '#fff3cd'
    
    # Display decision
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; margin: 10px 0;">
        <h3>{decision_color} {decision} - {confidence} Confidence</h3>
        <p><strong>Score:</strong> {score} (Bullish: {decision_data.get('bullish_signals', 0)}, Bearish: {decision_data.get('bearish_signals', 0)})</p>
        <p><strong>Reasoning:</strong> {reason}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Additional insights
    st.subheader("💡 Key Insights")
    
    # Risk assessment
    if confidence == 'High':
        risk_level = "Low to Medium"
    elif confidence == 'Medium':
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    st.write(f"**Risk Level:** {risk_level}")
    
    # Time horizon recommendation
    if decision == 'BUY':
        st.write("**Recommended Time Horizon:** Short to Medium term (1-4 weeks)")
        st.write("**Entry Strategy:** Consider gradual accumulation on dips")
    elif decision == 'SELL':
        st.write("**Recommended Time Horizon:** Immediate to Short term")
        st.write("**Exit Strategy:** Consider partial profit booking")
    else:
        st.write("**Recommended Action:** Wait for clearer signals")
        st.write("**Monitoring:** Watch for breakout or breakdown patterns")

def display_price_charts(symbol: str, tech_engine: PreMarketTechnicalAnalysisEngine):
    """Display interactive price charts with indicators."""
    
    st.subheader("📈 Price Charts")
    
    try:
        # Get daily data for charting
        data = tech_engine.get_ohlcv_data(symbol, period="3mo", interval="1d")
        
        if data.empty:
            st.warning("No chart data available")
            return
        
        # Create candlestick chart
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=['Price & Bollinger Bands', 'RSI', 'Volume'],
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add Bollinger Bands
        try:
            import ta
            bb = ta.volatility.BollingerBands(close=data['Close'])
            
            fig.add_trace(
                go.Scatter(x=data.index, y=bb.bollinger_hband(), name='BB Upper', line=dict(color='red', dash='dash')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=data.index, y=bb.bollinger_mavg(), name='BB Middle', line=dict(color='blue')),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=data.index, y=bb.bollinger_lband(), name='BB Lower', line=dict(color='red', dash='dash')),
                row=1, col=1
            )
        except:
            pass
        
        # RSI
        try:
            rsi = ta.momentum.RSIIndicator(close=data['Close'])
            fig.add_trace(
                go.Scatter(x=data.index, y=rsi.rsi(), name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            # Add RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        except:
            pass
        
        # Volume
        fig.add_trace(
            go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='lightblue'),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"{symbol} - Technical Analysis Chart",
            height=800,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="Volume", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating charts: {str(e)}")

def display_analysis_summary_table(results: List[Dict], show_ohlcv: bool, show_indicators: bool, show_decisions: bool):
    """Display summary table of analysis results."""
    
    if not results:
        st.warning("No analysis results to display")
        return
    
    # Create summary dataframe
    summary_data = []
    
    for result in results:
        try:
            symbol = result['symbol']
            analysis = result['analysis']
            decision = result['decision']
            tradingview_link = result['tradingview_link']
            
            row = {'Symbol': symbol}
            
            # Add OHLCV data
            if show_ohlcv and 'daily' in analysis['timeframes']:
                daily = analysis['timeframes']['daily']
                if 'ohlcv' in daily:
                    ohlcv = daily['ohlcv']
                    row.update({
                        'Price (₹)': ohlcv['close'],
                        'High (₹)': ohlcv['high'],
                        'Low (₹)': ohlcv['low'],
                        'Volume': format_volume(ohlcv['volume'])
                    })
            
            # Add indicators
            if show_indicators and 'daily' in analysis['timeframes'] and 'indicators' in analysis['timeframes']['daily']:
                daily_indicators = analysis['timeframes']['daily']['indicators']
                
                # Basic indicators
                rsi_val = daily_indicators.get('rsi', np.nan)
                adx_val = daily_indicators.get('adx', np.nan)
                
                # KST indicators
                kst_data = daily_indicators.get('kst', {})
                kst_val = kst_data.get('kst', np.nan) if isinstance(kst_data, dict) else np.nan
                
                # Relative strength indicators
                rs_data = daily_indicators.get('relative_strength', {})
                rs_val = rs_data.get('relative_strength', np.nan) if isinstance(rs_data, dict) else np.nan
                rs_rank = rs_data.get('rs_rank', np.nan) if isinstance(rs_data, dict) else np.nan
                outperformance = rs_data.get('outperformance', 'N/A') if isinstance(rs_data, dict) else 'N/A'
                
                row.update({
                    'Daily RSI': f"{rsi_val:.1f}" if not pd.isna(rsi_val) else 'N/A',
                    'Daily ADX': f"{adx_val:.1f}" if not pd.isna(adx_val) else 'N/A',
                    'KST': f"{kst_val:.1f}" if not pd.isna(kst_val) else 'N/A',
                    'Rel. Strength': f"{rs_val:.1f}%" if not pd.isna(rs_val) else 'N/A',
                    'RS Rank': f"{rs_rank:.0f}" if not pd.isna(rs_rank) else 'N/A',
                    'vs Benchmark': outperformance
                })
            elif show_indicators:
                # Add N/A values when indicators are not available
                row.update({
                    'Daily RSI': 'N/A',
                    'Daily ADX': 'N/A',
                    'KST': 'N/A',
                    'Rel. Strength': 'N/A',
                    'RS Rank': 'N/A',
                    'vs Benchmark': 'N/A'
                })
            
            # Add decision
            if show_decisions:
                row.update({
                    'Decision': decision['decision'],
                    'Confidence': decision['confidence'],
                    'Score': decision.get('score', 0)
                })
            
            # Add TradingView link (store URL for clickable display)
            row['TradingView'] = result['tradingview_link']
            
            summary_data.append(row)
            
        except Exception as e:
            st.warning(f"Error processing result for {result.get('symbol', 'Unknown')}: {str(e)}")
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        
        # Apply color coding for decisions
        def color_decision(val):
            if val == 'BUY':
                return 'background-color: #d4edda'
            elif val == 'SELL':
                return 'background-color: #f8d7da'
            else:
                return 'background-color: #fff3cd'
        
        # Configure columns for better display
        column_config = {}
        if 'TradingView' in df_summary.columns:
            column_config['TradingView'] = st.column_config.LinkColumn(
                "TradingView Chart",
                help="Click to view chart on TradingView",
                display_text="View Chart"
            )
        
        if 'Decision' in df_summary.columns:
            styled_df = df_summary.style.applymap(color_decision, subset=['Decision'])
            st.dataframe(styled_df, use_container_width=True, column_config=column_config)
        else:
            st.dataframe(df_summary, use_container_width=True, column_config=column_config)
        
        # Summary statistics
        if show_decisions and 'Decision' in df_summary.columns:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                buy_count = len(df_summary[df_summary['Decision'] == 'BUY'])
                st.metric("🟢 BUY Signals", buy_count)
            
            with col2:
                sell_count = len(df_summary[df_summary['Decision'] == 'SELL'])
                st.metric("🔴 SELL Signals", sell_count)
            
            with col3:
                hold_count = len(df_summary[df_summary['Decision'] == 'HOLD'])
                st.metric("🟡 HOLD Signals", hold_count)

def format_volume(volume: int) -> str:
    """Format volume in readable format."""
    if volume >= 10000000:  # 1 Crore
        return f"{volume/10000000:.1f}Cr"
    elif volume >= 100000:  # 1 Lakh
        return f"{volume/100000:.1f}L"
    elif volume >= 1000:  # 1 Thousand
        return f"{volume/1000:.1f}K"
    else:
        return str(volume)

# Main function for integration
def show_advanced_premarket_technical_analysis(kite=None):
    """Main function to be called from the main dashboard."""
    display_technical_analysis_dashboard(kite)
