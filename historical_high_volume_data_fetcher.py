"""
Historical High Volume Data Fetcher
===================================
Fetches historical stock data for closed market sessions, focusing on stocks
with highest trading activity from the last trading day or user-selected dates.

Features:
- Last trading day detection (excluding weekends/holidays)
- Historical volume analysis from Kite API and Yahoo Finance
- Date selection interface for custom analysis
- Pre-market preparation data

Author: AI Assistant for Indian Stock Market Analysis
Created: 2025-01-27
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
# Removed yfinance - using only Zerodha API
import streamlit as st
from kiteconnect import KiteConnect
from typing import List, Dict, Optional, Tuple
import calendar
import traceback

class HistoricalHighVolumeDataFetcher:
    """
    Fetches historical high-volume stock data for closed market sessions.
    """
    
    def __init__(self, kite: Optional[KiteConnect] = None):
        self.kite = kite
        self.min_volume = 75000
        self.nifty_500_symbols = self._get_nifty_500_symbols()
        
    def _get_nifty_500_symbols(self) -> List[str]:
        """Get list of Nifty 500 stock symbols."""
        return [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", "HDFC",
            "KOTAKBANK", "BHARTIARTL", "ITC", "SBIN", "LT", "ASIANPAINT", "AXISBANK",
            "MARUTI", "BAJFINANCE", "HCLTECH", "DMART", "SUNPHARMA", "TITAN",
            "ULTRACEMCO", "WIPRO", "NESTLEIND", "POWERGRID", "NTPC", "TECHM",
            "BAJAJFINSV", "ONGC", "TATAMOTORS", "DIVISLAB", "JSWSTEEL", "GRASIM",
            "HINDALCO", "ADANIENT", "CIPLA", "COALINDIA", "BRITANNIA", "DRREDDY",
            "EICHERMOT", "APOLLOHOSP", "BPCL", "TATACONSUM", "INDUSINDBK",
            "BAJAJ-AUTO", "HEROMOTOCO", "GODREJCP", "SBILIFE", "HDFCLIFE",
            "TATASTEEL", "PIDILITIND", "BERGEPAINT", "MARICO", "DABUR", "COLPAL",
            "MCDOWELL-N", "ADANIPORTS", "UPL", "GAIL", "VEDL", "SAIL", "NMDC",
            "BANKBARODA", "PNB", "CANBK", "UNIONBANK", "IDFCFIRSTB", "FEDERALBNK",
            "RBLBANK", "BANDHANBNK", "AUBANK", "INDIGO", "SPICEJET", "JUBLFOOD",
            "ZOMATO", "NYKAA", "PAYTM", "POLICYBZR", "STAR", "ZEEL", "SUNTV"
        ]
    
    def get_last_trading_day(self, from_date: date = None) -> date:
        """
        Get the last trading day (excluding weekends and common holidays).
        
        Args:
            from_date: Date to work backwards from (default: today)
            
        Returns:
            Last trading day as date object
        """
        if from_date is None:
            from_date = date.today()
        
        # Indian market holidays (major ones - in practice you'd use a holiday calendar API)
        indian_holidays_2025 = [
            date(2025, 1, 26),  # Republic Day
            date(2025, 3, 14),  # Holi
            date(2025, 4, 18),  # Good Friday
            date(2025, 8, 15),  # Independence Day
            date(2025, 10, 2),  # Gandhi Jayanti
            date(2025, 11, 1),  # Diwali (approximate)
        ]
        
        current_date = from_date
        
        while True:
            # Check if it's a weekend
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date -= timedelta(days=1)
                continue
            
            # Check if it's a holiday
            if current_date in indian_holidays_2025:
                current_date -= timedelta(days=1)
                continue
            
            # If we've gone back more than 10 days, just return the date
            if (from_date - current_date).days > 10:
                break
                
            return current_date
        
        # Fallback: return the date anyway
        return current_date
    
    def fetch_historical_data_kite(self, symbols: List[str], target_date: date) -> pd.DataFrame:
        """
        Fetch historical data using Kite API for a specific date.
        """
        if not self.kite:
            return pd.DataFrame()
        
        stock_data = []
        
        try:
            # Get instrument tokens
            instruments = self.kite.instruments("NSE")
            symbol_token_map = {inst['tradingsymbol']: inst['instrument_token'] 
                              for inst in instruments 
                              if inst['tradingsymbol'] in symbols}
            
            # Fetch historical data for each symbol
            for symbol in symbols:
                token = symbol_token_map.get(symbol)
                if not token:
                    continue
                
                try:
                    # Get historical data for the target date
                    historical_data = self.kite.historical_data(
                        instrument_token=token,
                        from_date=target_date,
                        to_date=target_date,
                        interval="day"
                    )
                    
                    if historical_data:
                        data = historical_data[0]  # Get the single day's data
                        volume = data.get('volume', 0)
                        
                        if volume >= self.min_volume:
                            open_price = data.get('open', 0)
                            close_price = data.get('close', 0)
                            high_price = data.get('high', 0)
                            low_price = data.get('low', 0)
                            
                            price_change = close_price - open_price
                            price_change_pct = (price_change / open_price * 100) if open_price > 0 else 0
                            
                            stock_data.append({
                                'symbol': symbol,
                                'current_price': close_price,
                                'volume': volume,
                                'price_change': price_change,
                                'price_change_pct': price_change_pct,
                                'high': high_price,
                                'low': low_price,
                                'open': open_price,
                                'close': close_price,
                                'date': target_date.strftime('%Y-%m-%d'),
                                'last_updated': datetime.now().strftime('%H:%M:%S')
                            })
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            st.error(f"Error fetching historical data from Kite: {str(e)}")
            return pd.DataFrame()
        
        return pd.DataFrame(stock_data)
    
    def fetch_historical_data_yfinance(self, symbols: List[str], target_date: date) -> pd.DataFrame:
        """
        Fetch historical data using Yahoo Finance for a specific date.
        """
        stock_data = []
        
        # Calculate date range (get a few days around target date for better data)
        start_date = target_date - timedelta(days=5)
        end_date = target_date + timedelta(days=1)
        
        for symbol in symbols:
            try:
                ticker = f"{symbol}.NS"
                stock = yf.Ticker(ticker)
                
                # Get historical data
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    continue
                
                # Find data for the target date (or closest available)
                target_data = None
                target_date_str = target_date.strftime('%Y-%m-%d')
                
                # Try exact date first
                for idx in hist.index:
                    if idx.strftime('%Y-%m-%d') == target_date_str:
                        target_data = hist.loc[idx]
                        break
                
                # If exact date not found, use the last available data
                if target_data is None and not hist.empty:
                    target_data = hist.iloc[-1]
                    actual_date = hist.index[-1].strftime('%Y-%m-%d')
                else:
                    actual_date = target_date_str
                
                if target_data is not None:
                    volume = int(target_data['Volume'])
                    
                    if volume >= self.min_volume:
                        open_price = float(target_data['Open'])
                        close_price = float(target_data['Close'])
                        high_price = float(target_data['High'])
                        low_price = float(target_data['Low'])
                        
                        price_change = close_price - open_price
                        price_change_pct = (price_change / open_price * 100) if open_price > 0 else 0
                        
                        stock_data.append({
                            'symbol': symbol,
                            'current_price': round(close_price, 2),
                            'volume': volume,
                            'price_change': round(price_change, 2),
                            'price_change_pct': round(price_change_pct, 2),
                            'high': round(high_price, 2),
                            'low': round(low_price, 2),
                            'open': round(open_price, 2),
                            'close': round(close_price, 2),
                            'date': actual_date,
                            'last_updated': datetime.now().strftime('%H:%M:%S')
                        })
                        
            except Exception as e:
                continue
        
        return pd.DataFrame(stock_data)
    
    def get_historical_high_volume_stocks(self, target_date: date = None) -> pd.DataFrame:
        """
        Get high volume stocks for a specific historical date.
        
        Args:
            target_date: Date to fetch data for (default: last trading day)
            
        Returns:
            DataFrame with historical high volume stock data
        """
        if target_date is None:
            target_date = self.get_last_trading_day()
        
        # Try Kite API first, fallback to Yahoo Finance
        if self.kite:
            df = self.fetch_historical_data_kite(self.nifty_500_symbols, target_date)
        else:
            # Use Kite API only - no yfinance fallback
            if self.kite:
                df = self.fetch_historical_data_kite(self.nifty_500_symbols, target_date)
            else:
                st.error("Zerodha API session required for data fetching")
                return pd.DataFrame()
        
        if df.empty:
            return df
        
        # Sort by volume (highest first)
        df = df.sort_values('volume', ascending=False)
        
        return df.reset_index(drop=True)
    
    def format_volume(self, volume: int) -> str:
        """Format volume in readable format (K, L, Cr)."""
        if volume >= 10000000:  # 1 Crore
            return f"{volume/10000000:.1f}Cr"
        elif volume >= 100000:  # 1 Lakh
            return f"{volume/100000:.1f}L"
        elif volume >= 1000:  # 1 Thousand
            return f"{volume/1000:.1f}K"
        else:
            return str(volume)
    
    def get_date_options(self) -> List[date]:
        """Get list of recent trading dates for selection."""
        dates = []
        current_date = date.today()
        
        # Get last 10 trading days
        for _ in range(15):  # Check 15 days to get 10 trading days
            if current_date.weekday() < 5:  # Monday to Friday
                dates.append(current_date)
            current_date -= timedelta(days=1)
            
            if len(dates) >= 10:
                break
        
        return dates

def display_historical_data_interface(kite: Optional[KiteConnect] = None):
    """
    Display historical data interface when market is closed.
    """
    st.markdown("### 📅 Historical High Volume Stock Analysis")
    st.info("🕐 Market is currently closed. Analyzing historical trading data for pre-market preparation.")
    
    # Initialize historical fetcher
    hist_fetcher = HistoricalHighVolumeDataFetcher(kite)
    
    # Date selection interface
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("#### 📊 Select Analysis Date")
        
        # Default to last trading day
        default_date = hist_fetcher.get_last_trading_day()
        
        # Date input
        selected_date = st.date_input(
            "Choose date for analysis:",
            value=default_date,
            max_value=date.today(),
            help="Select a trading day to analyze high-volume stocks"
        )
    
    with col2:
        st.markdown("#### 🎯 Quick Options")
        if st.button("📈 Last Trading Day"):
            selected_date = hist_fetcher.get_last_trading_day()
            st.rerun()
    
    with col3:
        st.markdown("#### 🔄 Actions")
        fetch_data = st.button("📊 Fetch Data", type="primary")
    
    # Display selected date info
    if selected_date:
        day_name = calendar.day_name[selected_date.weekday()]
        st.markdown(f"**Selected Date:** {selected_date.strftime('%Y-%m-%d')} ({day_name})")
        
        if selected_date.weekday() >= 5:
            st.warning("⚠️ Selected date is a weekend. Market was closed.")
        
        # Auto-fetch for last trading day, or when button is clicked
        if fetch_data or selected_date == default_date:
            with st.spinner(f"📊 Fetching high-volume stock data for {selected_date.strftime('%Y-%m-%d')}..."):
                
                # Fetch historical data
                df = hist_fetcher.get_historical_high_volume_stocks(selected_date)
                
                if df.empty:
                    st.error(f"❌ No data available for {selected_date.strftime('%Y-%m-%d')}. Try a different date.")
                    return
                
                # Display summary
                st.success(f"✅ Found {len(df)} high-volume stocks for {selected_date.strftime('%Y-%m-%d')}")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Stocks", len(df))
                
                with col2:
                    gainers = len(df[df['price_change_pct'] > 0])
                    st.metric("Gainers", gainers)
                
                with col3:
                    losers = len(df[df['price_change_pct'] < 0])
                    st.metric("Losers", losers)
                
                with col4:
                    total_volume = df['volume'].sum()
                    st.metric("Total Volume", hist_fetcher.format_volume(total_volume))
                
                # Data tabs
                tab1, tab2, tab3 = st.tabs(["🔥 Volume Leaders", "📈 Top Gainers", "📉 Top Losers"])
                
                with tab1:
                    st.markdown(f"#### Highest Volume Stocks - {selected_date.strftime('%Y-%m-%d')}")
                    
                    display_df = df.head(20).copy()
                    display_df['volume_formatted'] = display_df['volume'].apply(hist_fetcher.format_volume)
                    display_df['price_change_formatted'] = display_df.apply(
                        lambda x: f"₹{x['price_change']:+.2f} ({x['price_change_pct']:+.2f}%)", axis=1
                    )
                    
                    st.dataframe(
                        display_df[['symbol', 'close', 'volume_formatted', 'price_change_formatted', 'high', 'low', 'date']],
                        column_config={
                            'symbol': 'Symbol',
                            'close': st.column_config.NumberColumn('Close Price (₹)', format="₹%.2f"),
                            'volume_formatted': 'Volume',
                            'price_change_formatted': 'Change',
                            'high': st.column_config.NumberColumn('High (₹)', format="₹%.2f"),
                            'low': st.column_config.NumberColumn('Low (₹)', format="₹%.2f"),
                            'date': 'Date'
                        },
                        use_container_width=True
                    )
                
                with tab2:
                    st.markdown(f"#### Top Gainers - {selected_date.strftime('%Y-%m-%d')}")
                    
                    gainers_df = df[df['price_change_pct'] > 0].sort_values('price_change_pct', ascending=False).head(15)
                    
                    if not gainers_df.empty:
                        display_df = gainers_df.copy()
                        display_df['volume_formatted'] = display_df['volume'].apply(hist_fetcher.format_volume)
                        
                        st.dataframe(
                            display_df[['symbol', 'close', 'price_change_pct', 'volume_formatted', 'date']],
                            column_config={
                                'symbol': 'Symbol',
                                'close': st.column_config.NumberColumn('Close Price (₹)', format="₹%.2f"),
                                'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                                'volume_formatted': 'Volume',
                                'date': 'Date'
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("No gainers found for this date.")
                
                with tab3:
                    st.markdown(f"#### Top Losers - {selected_date.strftime('%Y-%m-%d')}")
                    
                    losers_df = df[df['price_change_pct'] < 0].sort_values('price_change_pct', ascending=True).head(15)
                    
                    if not losers_df.empty:
                        display_df = losers_df.copy()
                        display_df['volume_formatted'] = display_df['volume'].apply(hist_fetcher.format_volume)
                        
                        st.dataframe(
                            display_df[['symbol', 'close', 'price_change_pct', 'volume_formatted', 'date']],
                            column_config={
                                'symbol': 'Symbol',
                                'close': st.column_config.NumberColumn('Close Price (₹)', format="₹%.2f"),
                                'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                                'volume_formatted': 'Volume',
                                'date': 'Date'
                            },
                            use_container_width=True
                        )
                    else:
                        st.info("No losers found for this date.")
                
                # Analysis insights
                st.markdown("---")
                st.markdown("#### 💡 Pre-Market Insights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🎯 Key Observations:**")
                    avg_volume = df['volume'].mean()
                    max_volume_stock = df.iloc[0]
                    
                    st.markdown(f"- **Highest Volume:** {max_volume_stock['symbol']} ({hist_fetcher.format_volume(max_volume_stock['volume'])})")
                    st.markdown(f"- **Average Volume:** {hist_fetcher.format_volume(int(avg_volume))}")
                    st.markdown(f"- **Active Stocks:** {len(df)} stocks with >75K volume")
                
                with col2:
                    st.markdown("**📈 Market Sentiment:**")
                    gainer_pct = (gainers / len(df) * 100) if len(df) > 0 else 0
                    st.markdown(f"- **Bullish Stocks:** {gainers} ({gainer_pct:.1f}%)")
                    st.markdown(f"- **Bearish Stocks:** {losers} ({100-gainer_pct:.1f}%)")
                    
                    if gainer_pct > 60:
                        st.success("🟢 Overall bullish sentiment")
                    elif gainer_pct < 40:
                        st.error("🔴 Overall bearish sentiment")
                    else:
                        st.info("🟡 Mixed market sentiment")
                
                st.markdown(f"**📊 Data Source:** {'Zerodha Kite API' if kite else 'Yahoo Finance'}")
                st.markdown(f"**⏰ Analysis Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
