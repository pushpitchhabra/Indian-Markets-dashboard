"""
Enhanced Pre-Market Dashboard
============================
Comprehensive dashboard with fixed technical analysis, market indices ticker,
stock selection options, and live data integration.

Author: AI Assistant for Indian Stock Market Dashboard
Created: 2025-01-27
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from market_indices_tracker import show_market_indices_ticker
from stock_universe_manager import get_stock_universe_manager
from premarket_technical_analysis_engine import analyze_stock_for_premarket, PreMarketTechnicalAnalysisEngine

def display_enhanced_premarket_dashboard(kite=None):
    """
    Enhanced pre-market dashboard with all user-requested features.
    """
    st.title("🚀 Enhanced Pre-Market Technical Analysis Dashboard")
    st.markdown("*Real-time market data with comprehensive technical analysis*")
    
    # 1. MARKET INDICES TICKER (Always visible at top)
    show_market_indices_ticker()
    
    # Initialize components
    stock_manager = get_stock_universe_manager()
    tech_engine = PreMarketTechnicalAnalysisEngine(kite)
    
    # 2. STOCK SELECTION UI
    universe_name, stock_count, selected_stocks, analysis_mode = stock_manager.display_stock_selection_ui()
    
    # 3. ANALYSIS SETTINGS (Only for detailed analysis)
    if analysis_mode == "Detailed Analysis":
        st.subheader("⚙️ Advanced Analysis Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
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
        
        with col2:
            rs_period = st.number_input(
                "Relative Strength Period (days)",
                min_value=10,
                max_value=252,
                value=55,
                step=5,
                help="Number of days for relative strength calculation"
            )
    else:
        # Default settings for quick analysis
        benchmark_symbol = "^NSEI"
        rs_period = 55
    
    # 4. ANALYSIS EXECUTION
    if st.button("🔍 Start Analysis", type="primary", use_container_width=True):
        if not selected_stocks:
            st.error("No stocks selected for analysis!")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        with results_container:
            st.subheader(f"📊 Technical Analysis Results - {universe_name}")
            st.info(f"Analyzing {len(selected_stocks)} stocks from {universe_name} universe")
            
            # Results storage
            analysis_results = []
            
            # Process each stock
            for i, symbol in enumerate(selected_stocks):
                try:
                    # Update progress
                    progress = (i + 1) / len(selected_stocks)
                    progress_bar.progress(progress)
                    status_text.text(f"Analyzing {symbol}... ({i+1}/{len(selected_stocks)})")
                    
                    # Perform analysis
                    result = analyze_stock_for_premarket(
                        symbol=symbol,
                        kite=kite,
                        benchmark=benchmark_symbol,
                        rs_period=rs_period
                    )
                    
                    if result and 'analysis' in result:
                        analysis_results.append(result)
                    
                except Exception as e:
                    st.warning(f"Error analyzing {symbol}: {str(e)}")
                    continue
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            if analysis_results:
                display_analysis_results(analysis_results, analysis_mode)
            else:
                st.error("No analysis results generated. Please check your internet connection and try again.")

def display_analysis_results(results: List[Dict], analysis_mode: str):
    """Display comprehensive analysis results."""
    
    # Summary metrics
    st.subheader("📈 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    buy_signals = sum(1 for r in results if r.get('decision', {}).get('decision') == 'BUY')
    sell_signals = sum(1 for r in results if r.get('decision', {}).get('decision') == 'SELL')
    hold_signals = sum(1 for r in results if r.get('decision', {}).get('decision') == 'HOLD')
    
    with col1:
        st.metric("🟢 BUY Signals", buy_signals)
    with col2:
        st.metric("🔴 SELL Signals", sell_signals)
    with col3:
        st.metric("🟡 HOLD Signals", hold_signals)
    with col4:
        st.metric("📊 Total Analyzed", len(results))
    
    # Detailed results table
    st.subheader("📋 Detailed Analysis Results")
    
    # Prepare data for table
    table_data = []
    
    for result in results:
        try:
            symbol = result.get('symbol', 'N/A')
            analysis = result.get('analysis', {})
            decision = result.get('decision', {})
            
            # Get daily timeframe data
            daily_data = analysis.get('timeframes', {}).get('daily', {})
            indicators = daily_data.get('indicators', {})
            ohlcv = daily_data.get('ohlcv', {})
            
            # Extract indicator values
            rsi_val = indicators.get('rsi', np.nan)
            adx_val = indicators.get('adx', np.nan)
            
            # KST data
            kst_data = indicators.get('kst', {})
            kst_val = kst_data.get('kst', np.nan) if isinstance(kst_data, dict) else np.nan
            
            # Relative strength data
            rs_data = indicators.get('relative_strength', {})
            rs_val = rs_data.get('relative_strength', np.nan) if isinstance(rs_data, dict) else np.nan
            rs_rank = rs_data.get('rs_rank', np.nan) if isinstance(rs_data, dict) else np.nan
            outperformance = rs_data.get('outperformance', 'N/A') if isinstance(rs_data, dict) else 'N/A'
            
            # Get index information for this stock
            stock_manager = get_stock_universe_manager()
            index_info = stock_manager.get_stock_index_info(symbol)
            primary_index = index_info.get('primary_index', 'N/A')
            weightage = index_info.get('weightage', 0.0)
            
            # Build row data with index information
            row = {
                'Symbol': symbol,
                'Index': primary_index if primary_index != 'N/A' else 'Multiple',
                'Weightage %': f"{weightage:.1f}%" if weightage > 0 else 'N/A',
                'Price': f"₹{ohlcv.get('close', 0):.2f}" if ohlcv.get('close') else 'N/A',
                'Volume': format_volume(ohlcv.get('volume', 0)) if ohlcv.get('volume') else 'N/A',
                'Daily RSI': f"{rsi_val:.1f}" if not pd.isna(rsi_val) else 'N/A',
                'Daily ADX': f"{adx_val:.1f}" if not pd.isna(adx_val) else 'N/A',
                'Decision': decision.get('decision', 'HOLD'),
                'Confidence': decision.get('confidence', 'Low'),
                'Score': decision.get('score', 0),
                'TradingView': result.get('tradingview_link', '#')
            }
            
            # Add detailed indicators only for detailed analysis
            if analysis_mode == "Detailed Analysis":
                row.update({
                    'KST': f"{kst_val:.1f}" if not pd.isna(kst_val) else 'N/A',
                    'Rel. Strength': f"{rs_val:.1f}%" if not pd.isna(rs_val) else 'N/A',
                    'RS Rank': f"{rs_rank:.0f}" if not pd.isna(rs_rank) else 'N/A',
                    'vs Benchmark': outperformance
                })
            
            table_data.append(row)
            
        except Exception as e:
            st.warning(f"Error processing result: {str(e)}")
            continue
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # Configure columns for better display
        column_config = {
            'TradingView': st.column_config.LinkColumn(
                "TradingView Chart",
                help="Click to view chart on TradingView",
                display_text="View Chart"
            )
        }
        
        # Apply styling
        def color_decision(val):
            if val == 'BUY':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'SELL':
                return 'background-color: #f8d7da; color: #721c24'
            else:
                return 'background-color: #fff3cd; color: #856404'
        
        styled_df = df.style.applymap(color_decision, subset=['Decision'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            column_config=column_config,
            hide_index=True
        )
        
        # Export options
        st.subheader("📤 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name=f"technical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.button("🔄 Refresh Analysis"):
                st.rerun()
    
    else:
        st.error("No valid analysis results to display.")

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

def show_enhanced_premarket_dashboard(kite=None):
    """Main function to be called from the main dashboard."""
    display_enhanced_premarket_dashboard(kite)
