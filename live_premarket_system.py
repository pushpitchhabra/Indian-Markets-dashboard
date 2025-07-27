"""
Live Pre-Market System
=====================
Real-time pre-market data streaming with live/stop toggle and refresh controls.
Respects Zerodha API rate limits and provides smooth user experience.

Features:
- Live streaming during pre-market hours (9:00-9:15 AM)
- Start/Stop toggle for manual control
- Configurable refresh intervals (30s, 60s, 120s)
- API rate limiting and error handling
- Progress indicators and status updates
- Historical fallback when market closed
"""

import streamlit as st
import pandas as pd
from datetime import datetime, time, date, timedelta
from kiteconnect import KiteConnect
import time as time_module
import threading
from typing import List, Dict, Optional
import logging

class LivePreMarketSystem:
    """
    Manages live pre-market data streaming with user controls.
    """
    
    def __init__(self, kite: KiteConnect):
        self.kite = kite
        self.is_streaming = False
        self.refresh_interval = 60  # Default 60 seconds
        self.api_call_count = 0
        self.api_limit_per_minute = 100  # Conservative limit
        self.last_reset_time = datetime.now()
        
    def get_market_session(self) -> tuple:
        """
        Get current market session status.
        Returns: (session, message, is_live_possible)
        """
        now = datetime.now()
        current_time = now.time()
        is_weekday = now.weekday() < 5
        
        # Market timings
        pre_market_start = time(9, 0)
        market_open = time(9, 15)
        market_close = time(15, 30)
        post_market_end = time(16, 0)
        
        if not is_weekday:
            return "closed", "🔴 Weekend - Market Closed", False
        
        if current_time < pre_market_start:
            return "before_premarket", "🌙 Before Pre-Market", False
        elif pre_market_start <= current_time < market_open:
            return "pre_market", "🟡 Pre-Market Session (LIVE POSSIBLE)", True
        elif market_open <= current_time < market_close:
            return "live_market", "🟢 Market Live", True
        elif market_close <= current_time < post_market_end:
            return "post_market", "🟡 Post-Market Session", True
        else:
            return "after_hours", "🔴 After Hours - Market Closed", False
    
    def check_api_limits(self) -> bool:
        """
        Check if we're within API rate limits.
        Reset counter every minute.
        """
        now = datetime.now()
        if (now - self.last_reset_time).seconds >= 60:
            self.api_call_count = 0
            self.last_reset_time = now
        
        return self.api_call_count < self.api_limit_per_minute
    
    def fetch_live_data(self, symbols: List[str]) -> pd.DataFrame:
        """
        Fetch live data for given symbols with rate limiting.
        """
        if not self.check_api_limits():
            st.warning("⚠️ API rate limit reached. Waiting...")
            return pd.DataFrame()
        
        try:
            live_data = []
            
            # Batch process symbols to reduce API calls
            batch_size = 20
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                
                # Create instrument keys for batch quote
                instrument_keys = [f"NSE:{symbol}" for symbol in batch]
                
                # Get quotes for batch
                quotes = self.kite.quote(instrument_keys)
                self.api_call_count += 1
                
                for symbol in batch:
                    key = f"NSE:{symbol}"
                    if key in quotes:
                        quote_data = quotes[key]
                        
                        live_data.append({
                            'Symbol': symbol,
                            'LTP': quote_data.get('last_price', 0),
                            'Open': quote_data.get('ohlc', {}).get('open', 0),
                            'High': quote_data.get('ohlc', {}).get('high', 0),
                            'Low': quote_data.get('ohlc', {}).get('low', 0),
                            'Close': quote_data.get('ohlc', {}).get('close', 0),
                            'Volume': quote_data.get('volume', 0),
                            'Change': quote_data.get('net_change', 0),
                            'Change %': round(quote_data.get('net_change', 0) / quote_data.get('ohlc', {}).get('close', 1) * 100, 2),
                            'Timestamp': datetime.now().strftime('%H:%M:%S')
                        })
                
                # Small delay between batches to be respectful
                time_module.sleep(0.1)
            
            return pd.DataFrame(live_data)
            
        except Exception as e:
            st.error(f"❌ Error fetching live data: {str(e)}")
            return pd.DataFrame()
    
    def get_default_symbols(self) -> List[str]:
        """Get default symbols for pre-market analysis"""
        return [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "INFY", "ITC", "SBIN",
            "BHARTIARTL", "KOTAKBANK", "LT", "HCLTECH", "ASIANPAINT", "AXISBANK", "MARUTI",
            "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "BAJFINANCE", "WIPRO", "M&M",
            "NTPC", "TECHM", "POWERGRID", "TATAMOTORS", "COALINDIA", "BAJAJFINSV", "HDFCLIFE"
        ]
    
    def display_live_controls(self):
        """Display live streaming controls"""
        st.subheader("🎛️ Live Streaming Controls")
        
        session, message, is_live_possible = self.get_market_session()
        
        # Market status
        if is_live_possible:
            st.markdown(f"""
            <div style="padding: 10px; background-color: #d4edda; border-radius: 5px; margin: 10px 0;">
                <strong>{message}</strong><br>
                Live streaming is available!
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding: 10px; background-color: #f8d7da; border-radius: 5px; margin: 10px 0;">
                <strong>{message}</strong><br>
                Live streaming not available. Historical data will be shown.
            </div>
            """, unsafe_allow_html=True)
        
        # Controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if is_live_possible:
                if st.button("▶️ Start Live" if not self.is_streaming else "⏸️ Stop Live", 
                           type="primary" if not self.is_streaming else "secondary"):
                    self.is_streaming = not self.is_streaming
                    if self.is_streaming:
                        st.success("✅ Live streaming started!")
                    else:
                        st.info("⏸️ Live streaming stopped")
            else:
                st.button("▶️ Start Live", disabled=True, help="Not available outside market hours")
        
        with col2:
            self.refresh_interval = st.selectbox(
                "Refresh Interval",
                [30, 60, 120, 300],
                index=1,
                format_func=lambda x: f"{x}s"
            )
        
        with col3:
            if st.button("🔄 Manual Refresh"):
                st.rerun()
        
        with col4:
            st.metric("API Calls", f"{self.api_call_count}/100")
        
        return is_live_possible
    
    def display_live_data(self, symbols: List[str]):
        """Display live or historical data based on market session"""
        session, message, is_live_possible = self.get_market_session()
        
        if is_live_possible and self.is_streaming:
            # Live data
            st.subheader("📊 Live Market Data")
            
            # Create placeholder for live updates
            data_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # Fetch and display live data
            with st.spinner("Fetching live data..."):
                live_df = self.fetch_live_data(symbols)
                
                if not live_df.empty:
                    # Sort by change % descending
                    live_df_sorted = live_df.sort_values('Change %', ascending=False)
                    
                    # Display data
                    data_placeholder.dataframe(
                        live_df_sorted,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Status update
                    status_placeholder.success(f"✅ Live data updated at {datetime.now().strftime('%H:%M:%S')} | Next update in {self.refresh_interval}s")
                    
                    # Auto-refresh if streaming
                    if self.is_streaming:
                        time_module.sleep(self.refresh_interval)
                        st.rerun()
                else:
                    status_placeholder.error("❌ No live data available")
        
        else:
            # Historical data fallback
            st.subheader("📊 Historical Market Data")
            st.info(f"💡 {message} - Showing historical data")
            
            self.display_historical_data(symbols)
    
    def display_historical_data(self, symbols: List[str]):
        """Display historical data when live is not available"""
        try:
            # Date selection
            col1, col2 = st.columns(2)
            
            with col1:
                selected_date = st.date_input(
                    "Select Date",
                    value=self.get_last_trading_day(),
                    max_value=date.today(),
                    key="live_premarket_historical_date"
                )
            
            with col2:
                if st.button("📈 Fetch Historical Data"):
                    with st.spinner("Fetching historical data..."):
                        historical_df = self.fetch_historical_data(symbols, selected_date)
                        
                        if not historical_df.empty:
                            st.success(f"✅ Fetched data for {len(historical_df)} stocks")
                            
                            # Calculate metrics
                            historical_df['Change %'] = ((historical_df['Close'] - historical_df['Open']) / historical_df['Open'] * 100).round(2)
                            historical_df['Volume (L)'] = (historical_df['Volume'] / 100000).round(2)
                            
                            # Sort by volume
                            historical_df_sorted = historical_df.sort_values('Volume', ascending=False)
                            
                            # Display data
                            st.dataframe(
                                historical_df_sorted[['Symbol', 'Open', 'High', 'Low', 'Close', 'Change %', 'Volume (L)']],
                                use_container_width=True
                            )
                            
                            # Basic statistics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Total Stocks", len(historical_df))
                            with col2:
                                gainers = len(historical_df[historical_df['Change %'] > 0])
                                st.metric("Gainers", gainers)
                            with col3:
                                losers = len(historical_df[historical_df['Change %'] < 0])
                                st.metric("Losers", losers)
                            with col4:
                                avg_volume = historical_df['Volume (L)'].mean()
                                st.metric("Avg Volume (L)", f"{avg_volume:.2f}")
                        else:
                            st.error("❌ No historical data available")
        
        except Exception as e:
            st.error(f"❌ Error displaying historical data: {str(e)}")
    
    def fetch_historical_data(self, symbols: List[str], target_date: date) -> pd.DataFrame:
        """Fetch historical data for given date"""
        try:
            historical_data = []
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(symbols[:20]):  # Limit for performance
                try:
                    # Get instrument token
                    instruments = self.kite.instruments("NSE")
                    instrument = next((inst for inst in instruments if inst['tradingsymbol'] == symbol), None)
                    
                    if instrument:
                        # Get historical data
                        hist_data = self.kite.historical_data(
                            instrument['instrument_token'],
                            target_date,
                            target_date,
                            "day"
                        )
                        
                        if hist_data:
                            data = hist_data[-1]
                            historical_data.append({
                                'Symbol': symbol,
                                'Open': data['open'],
                                'High': data['high'],
                                'Low': data['low'],
                                'Close': data['close'],
                                'Volume': data['volume'],
                                'Date': data['date'].strftime('%Y-%m-%d')
                            })
                    
                    progress_bar.progress((i + 1) / len(symbols[:20]))
                    
                except Exception as e:
                    continue
            
            progress_bar.empty()
            return pd.DataFrame(historical_data)
            
        except Exception as e:
            st.error(f"❌ Error fetching historical data: {str(e)}")
            return pd.DataFrame()
    
    def get_last_trading_day(self) -> date:
        """Get the last trading day (excluding weekends)"""
        today = date.today()
        days_back = 1
        
        while True:
            check_date = today - timedelta(days=days_back)
            if check_date.weekday() < 5:  # Monday=0, Sunday=6
                return check_date
            days_back += 1
            if days_back > 7:  # Safety check
                return today - timedelta(days=1)

def display_live_premarket_tab(kite: KiteConnect):
    """
    Display the live pre-market analysis tab.
    """
    st.header("🌅 Live Pre-Market Analysis")
    
    # Initialize live system
    if 'live_premarket_system' not in st.session_state:
        st.session_state.live_premarket_system = LivePreMarketSystem(kite)
    
    live_system = st.session_state.live_premarket_system
    
    # Display controls
    is_live_possible = live_system.display_live_controls()
    
    # Symbol selection
    st.subheader("📋 Stock Selection")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Option to use custom universe or default
        if 'instrument_universe' in st.session_state:
            use_custom = st.checkbox("Use Custom Instrument Universe", value=False)
            if use_custom:
                universe_df = st.session_state.instrument_universe
                symbols = universe_df['symbol'].tolist()[:50]  # Limit for performance
                st.info(f"📊 Using {len(symbols)} symbols from custom universe")
            else:
                symbols = live_system.get_default_symbols()
                st.info(f"📊 Using {len(symbols)} default Nifty symbols")
        else:
            symbols = live_system.get_default_symbols()
            st.info(f"📊 Using {len(symbols)} default Nifty symbols")
    
    with col2:
        symbol_limit = st.number_input(
            "Symbol Limit",
            min_value=10,
            max_value=100,
            value=30,
            help="Limit symbols to avoid API rate limits"
        )
        symbols = symbols[:symbol_limit]
    
    # Display live/historical data
    live_system.display_live_data(symbols)
    
    # Additional info
    st.markdown("---")
    st.markdown("""
    **💡 Live Pre-Market Features:**
    - ✅ Real-time data during pre-market hours (9:00-9:15 AM)
    - ✅ Configurable refresh intervals (30s to 5min)
    - ✅ API rate limiting to stay within Zerodha limits
    - ✅ Automatic fallback to historical data when market closed
    - ✅ Manual start/stop controls
    - ✅ Progress indicators and status updates
    """)
