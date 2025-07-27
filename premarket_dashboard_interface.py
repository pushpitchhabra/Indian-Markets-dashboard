"""
Pre-Market Dashboard Interface
==============================
Streamlit interface specifically designed for pre-market analysis and preparation.
Provides intuitive UI for analyzing high-volume stocks from previous trading sessions
to help with pre-market planning and decision making.

Features:
- Pre-market focused stock analysis interface
- Last trading day data with date selection
- Pre-market preparation insights and recommendations
- Volume leaders and price action analysis
- Pre-market scoring system for stock prioritization

Author: AI Assistant for Indian Stock Market Pre-Market Analysis
Created: 2025-01-27
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from typing import Optional
from kiteconnect import KiteConnect
from premarket_high_volume_analyzer import PreMarketHighVolumeAnalyzer

def display_premarket_analysis_interface(kite: Optional[KiteConnect] = None):
    """
    Main interface for pre-market analysis when market is closed.
    Specifically designed for pre-market preparation and planning.
    """
    st.markdown("### 🌅 Pre-Market High Volume Stock Analysis")
    
    # Pre-market session indicator
    analyzer = PreMarketHighVolumeAnalyzer(kite)
    is_premarket = analyzer.is_premarket_session()
    
    if is_premarket:
        st.success("🟢 Pre-Market Session Active (9:00 AM - 9:15 AM)")
        st.info("💡 Use this data to prepare for the upcoming market session!")
    else:
        st.info("🕐 Market is closed. Analyzing previous trading session data for pre-market preparation.")
    
    # Header with key info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Select Analysis Date")
        default_date = analyzer.get_last_trading_day()
        
        selected_date = st.date_input(
            "Choose trading day for pre-market analysis:",
            value=default_date,
            max_value=date.today(),
            help="Select a trading day to analyze for pre-market preparation"
        )
    
    with col2:
        st.markdown("#### 🎯 Quick Actions")
        if st.button("📈 Last Trading Day", help="Analyze most recent trading day"):
            selected_date = default_date
            st.rerun()
    
    with col3:
        st.markdown("#### 🔄 Analysis")
        analyze_button = st.button("🚀 Analyze for Pre-Market", type="primary")
    
    # Display selected date information
    if selected_date:
        day_name = calendar.day_name[selected_date.weekday()]
        st.markdown(f"**📅 Analysis Date:** {selected_date.strftime('%Y-%m-%d')} ({day_name})")
        
        if selected_date.weekday() >= 5:
            st.warning("⚠️ Selected date is a weekend. Market was closed.")
            return
        
        # Auto-analyze for default date or when button clicked
        if analyze_button or selected_date == default_date:
            _display_premarket_analysis_results(analyzer, selected_date, kite)

def _display_premarket_analysis_results(analyzer: PreMarketHighVolumeAnalyzer, 
                                       selected_date: date, 
                                       kite: Optional[KiteConnect] = None):
    """Display the pre-market analysis results."""
    
    with st.spinner(f"🔍 Analyzing pre-market data for {selected_date.strftime('%Y-%m-%d')}..."):
        
        # Fetch pre-market analysis data
        df = analyzer.get_premarket_high_volume_stocks(selected_date)
        
        if df.empty:
            st.error(f"❌ No pre-market data available for {selected_date.strftime('%Y-%m-%d')}. Try a different date.")
            return
        
        # Generate insights
        insights = analyzer.get_premarket_insights(df)
        
        # Success message
        st.success(f"✅ Pre-market analysis complete! Found {len(df)} high-volume stocks for preparation.")
        
        # Key Pre-Market Metrics
        st.markdown("#### 🎯 Pre-Market Preparation Dashboard")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "📊 Active Stocks", 
                insights.get('total_stocks', 0),
                help="Stocks with volume > 75K"
            )
        
        with col2:
            st.metric(
                "🔥 Very High Volume", 
                insights.get('very_high_volume_count', 0),
                help="Stocks with 50L+ volume"
            )
        
        with col3:
            st.metric(
                "📈 Big Movers", 
                insights.get('big_movers_count', 0),
                help="Stocks with 3%+ price moves"
            )
        
        with col4:
            st.metric(
                "⚡ High Volatility", 
                insights.get('high_volatility_count', 0),
                help="Stocks with 5%+ volatility"
            )
        
        with col5:
            avg_vol = insights.get('avg_volume', 0)
            st.metric(
                "📊 Avg Volume", 
                analyzer.format_volume(int(avg_vol)),
                help="Average volume across all stocks"
            )
        
        # Top Pre-Market Stock Highlight
        if insights.get('top_premarket_stock'):
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### 🏆 Top Pre-Market Focus Stock")
                top_stock = insights['top_premarket_stock']
                top_score = insights['top_score']
                
                st.markdown(f"""
                <div style="padding: 1rem; background-color: #f0f8ff; border-left: 4px solid #1f77b4; border-radius: 5px;">
                    <h3 style="color: #1f77b4; margin: 0;">{top_stock}</h3>
                    <p style="margin: 0.5rem 0;"><strong>Pre-Market Score:</strong> {top_score}/100</p>
                    <p style="margin: 0; color: #666;">Highest priority for pre-market analysis</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 💡 Pre-Market Tip")
                if top_score >= 80:
                    st.success("🎯 Extremely high interest - monitor closely!")
                elif top_score >= 60:
                    st.info("📊 High interest - good for pre-market focus")
                else:
                    st.warning("⚠️ Moderate interest - consider other options")
        
        # Pre-Market Analysis Tabs
        st.markdown("---")
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Pre-Market Priorities", 
            "🔥 Volume Leaders", 
            "📈 Price Movers", 
            "💡 Pre-Market Insights"
        ])
        
        with tab1:
            st.markdown(f"#### 🎯 Top Pre-Market Priority Stocks - {selected_date.strftime('%Y-%m-%d')}")
            st.markdown("*Ranked by Pre-Market Score (Volume + Price Movement + Volatility)*")
            
            priority_df = df.head(15).copy()
            priority_df['volume_formatted'] = priority_df['volume'].apply(analyzer.format_volume)
            priority_df['price_change_formatted'] = priority_df.apply(
                lambda x: f"₹{x['price_change']:+.2f} ({x['price_change_pct']:+.2f}%)", axis=1
            )
            
            st.dataframe(
                priority_df[['symbol', 'premarket_score', 'close_price', 'volume_formatted', 
                           'price_change_formatted', 'volatility_pct', 'volume_category']],
                column_config={
                    'symbol': 'Symbol',
                    'premarket_score': st.column_config.NumberColumn('Pre-Market Score', format="%.1f"),
                    'close_price': st.column_config.NumberColumn('Close Price (₹)', format="₹%.2f"),
                    'volume_formatted': 'Volume',
                    'price_change_formatted': 'Price Change',
                    'volatility_pct': st.column_config.NumberColumn('Volatility %', format="%.2f%%"),
                    'volume_category': 'Volume Category'
                },
                use_container_width=True
            )
        
        with tab2:
            st.markdown(f"#### 🔥 Volume Leaders - {selected_date.strftime('%Y-%m-%d')}")
            st.markdown("*Stocks with highest trading volume - ideal for pre-market liquidity*")
            
            volume_leaders = df.sort_values('volume', ascending=False).head(20)
            display_df = volume_leaders.copy()
            display_df['volume_formatted'] = display_df['volume'].apply(analyzer.format_volume)
            
            st.dataframe(
                display_df[['symbol', 'volume_formatted', 'close_price', 'premarket_score', 'volume_category']],
                column_config={
                    'symbol': 'Symbol',
                    'volume_formatted': 'Volume',
                    'close_price': st.column_config.NumberColumn('Close Price (₹)', format="₹%.2f"),
                    'premarket_score': st.column_config.NumberColumn('Pre-Market Score', format="%.1f"),
                    'volume_category': 'Volume Category'
                },
                use_container_width=True
            )
        
        with tab3:
            st.markdown(f"#### 📈 Significant Price Movers - {selected_date.strftime('%Y-%m-%d')}")
            st.markdown("*Stocks with notable price movements - watch for continuation/reversal*")
            
            # Split into gainers and losers
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🟢 Top Gainers")
                gainers = df[df['price_change_pct'] > 0].sort_values('price_change_pct', ascending=False).head(10)
                
                if not gainers.empty:
                    st.dataframe(
                        gainers[['symbol', 'price_change_pct', 'close_price', 'premarket_score']],
                        column_config={
                            'symbol': 'Symbol',
                            'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                            'close_price': st.column_config.NumberColumn('Close (₹)', format="₹%.2f"),
                            'premarket_score': st.column_config.NumberColumn('Score', format="%.1f")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No gainers found")
            
            with col2:
                st.markdown("##### 🔴 Top Losers")
                losers = df[df['price_change_pct'] < 0].sort_values('price_change_pct', ascending=True).head(10)
                
                if not losers.empty:
                    st.dataframe(
                        losers[['symbol', 'price_change_pct', 'close_price', 'premarket_score']],
                        column_config={
                            'symbol': 'Symbol',
                            'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                            'close_price': st.column_config.NumberColumn('Close (₹)', format="₹%.2f"),
                            'premarket_score': st.column_config.NumberColumn('Score', format="%.1f")
                        },
                        use_container_width=True
                    )
                else:
                    st.info("No losers found")
        
        with tab4:
            st.markdown(f"#### 💡 Pre-Market Preparation Insights - {selected_date.strftime('%Y-%m-%d')}")
            
            # Market sentiment analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 📊 Market Sentiment Analysis")
                
                gainers_count = len(df[df['price_change_pct'] > 0])
                losers_count = len(df[df['price_change_pct'] < 0])
                total_stocks = len(df)
                
                if total_stocks > 0:
                    bullish_pct = (gainers_count / total_stocks) * 100
                    
                    st.markdown(f"- **Bullish Stocks:** {gainers_count} ({bullish_pct:.1f}%)")
                    st.markdown(f"- **Bearish Stocks:** {losers_count} ({100-bullish_pct:.1f}%)")
                    
                    if bullish_pct > 60:
                        st.success("🟢 **Overall Bullish Sentiment** - Consider long positions")
                    elif bullish_pct < 40:
                        st.error("🔴 **Overall Bearish Sentiment** - Exercise caution")
                    else:
                        st.info("🟡 **Mixed Sentiment** - Stock-specific analysis needed")
            
            with col2:
                st.markdown("##### 🎯 Pre-Market Recommendations")
                
                # Volume-based recommendations
                very_high_vol = insights.get('very_high_volume_count', 0)
                big_movers = insights.get('big_movers_count', 0)
                
                st.markdown("**Focus Areas:**")
                
                if very_high_vol > 0:
                    st.markdown(f"- 🔥 **{very_high_vol} stocks** with very high volume - excellent liquidity")
                
                if big_movers > 0:
                    st.markdown(f"- 📈 **{big_movers} stocks** with 3%+ moves - momentum plays")
                
                if insights.get('high_volatility_count', 0) > 0:
                    st.markdown(f"- ⚡ **{insights['high_volatility_count']} stocks** with high volatility - risk/reward opportunities")
                
                # Top 3 recommendations
                st.markdown("**Top 3 Pre-Market Picks:**")
                top_3 = df.head(3)
                for i, (_, stock) in enumerate(top_3.iterrows(), 1):
                    st.markdown(f"{i}. **{stock['symbol']}** (Score: {stock['premarket_score']:.1f})")
        
        # Footer information
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**📊 Data Source:** {'Zerodha Kite API' if kite else 'Yahoo Finance'}")
        
        with col2:
            st.markdown(f"**📅 Analysis Date:** {selected_date.strftime('%Y-%m-%d')}")
        
        with col3:
            st.markdown(f"**⏰ Generated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Pre-market preparation tips
        with st.expander("💡 Pre-Market Preparation Tips"):
            st.markdown("""
            **🌅 Pre-Market Success Tips:**
            
            1. **Focus on High-Score Stocks** - Prioritize stocks with pre-market scores above 60
            2. **Check Volume Categories** - 'Very High' and 'High' volume stocks offer better liquidity
            3. **Monitor Price Movers** - Stocks with 3%+ moves may continue the trend
            4. **Watch Volatility** - High volatility stocks offer more trading opportunities but higher risk
            5. **Plan Entry/Exit** - Use this data to set your pre-market and opening bell strategy
            
            **⚠️ Risk Management:**
            - Always use stop losses in pre-market trading
            - Pre-market volumes are typically lower than regular hours
            - News and events can significantly impact pre-market prices
            """)

def display_premarket_quick_view(kite: Optional[KiteConnect] = None):
    """
    Quick pre-market view for the sidebar or compact display.
    """
    analyzer = PreMarketHighVolumeAnalyzer(kite)
    
    with st.expander("🌅 Pre-Market Quick View"):
        last_trading_day = analyzer.get_last_trading_day()
        
        st.markdown(f"**Last Trading Day:** {last_trading_day.strftime('%Y-%m-%d')}")
        
        if analyzer.is_premarket_session():
            st.success("🟢 Pre-Market Active")
        else:
            st.info("🕐 Market Closed")
        
        if st.button("📊 Full Pre-Market Analysis", key="quick_premarket"):
            st.session_state.show_premarket = True
