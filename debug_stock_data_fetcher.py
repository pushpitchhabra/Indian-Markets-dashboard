"""
Debug Stock Data Fetcher
========================
A debug version to identify why stocks are not showing up in the dashboard.
This will test both Kite API and Yahoo Finance fallback methods.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, time
import streamlit as st
from kiteconnect import KiteConnect
from typing import List, Dict, Optional
import traceback

class DebugStockDataFetcher:
    """Debug version of the stock data fetcher to identify issues."""
    
    def __init__(self, kite: Optional[KiteConnect] = None):
        self.kite = kite
        self.min_volume = 75000
        # Use a smaller set of reliable stocks for testing
        self.test_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", 
            "ICICIBANK", "BHARTIARTL", "ITC", "SBIN", "LT"
        ]
        
    def test_yahoo_finance_single_stock(self, symbol: str) -> Dict:
        """Test fetching data for a single stock using Yahoo Finance."""
        try:
            ticker = f"{symbol}.NS"
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            
            # Get recent history
            hist = stock.history(period="5d", interval="1d")  # Get 5 days of data
            
            if hist.empty:
                return {
                    'symbol': symbol,
                    'status': 'FAILED',
                    'error': 'No historical data available',
                    'data': None
                }
            
            # Get the latest available data
            latest_data = hist.iloc[-1]
            
            # Calculate volume (use latest day's volume)
            volume = int(latest_data['Volume']) if 'Volume' in latest_data else 0
            
            # Calculate price change
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                current_price = latest_data['Close']
                price_change = current_price - prev_close
                price_change_pct = (price_change / prev_close) * 100
            else:
                current_price = latest_data['Close']
                price_change = 0
                price_change_pct = 0
            
            return {
                'symbol': symbol,
                'status': 'SUCCESS',
                'current_price': round(float(current_price), 2),
                'volume': volume,
                'price_change': round(float(price_change), 2),
                'price_change_pct': round(float(price_change_pct), 2),
                'high': round(float(latest_data['High']), 2),
                'low': round(float(latest_data['Low']), 2),
                'last_updated': datetime.now().strftime('%H:%M:%S'),
                'data_date': hist.index[-1].strftime('%Y-%m-%d'),
                'meets_volume_criteria': volume >= self.min_volume
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'status': 'ERROR',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def test_all_yahoo_finance(self) -> pd.DataFrame:
        """Test Yahoo Finance for all test symbols."""
        results = []
        
        st.write("🔍 Testing Yahoo Finance data fetching...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(self.test_symbols):
            status_text.text(f"Testing {symbol}...")
            result = self.test_yahoo_finance_single_stock(symbol)
            results.append(result)
            progress_bar.progress((i + 1) / len(self.test_symbols))
        
        status_text.text("Testing complete!")
        
        return pd.DataFrame(results)
    
    def test_kite_connection(self) -> Dict:
        """Test Kite API connection and data fetching."""
        if not self.kite:
            return {
                'status': 'NO_KITE',
                'message': 'No Kite connection available'
            }
        
        try:
            # Test basic connection
            profile = self.kite.profile()
            
            # Test instruments fetch
            instruments = self.kite.instruments("NSE")
            
            # Find test symbols in instruments
            found_symbols = []
            for symbol in self.test_symbols:
                found = [inst for inst in instruments if inst['tradingsymbol'] == symbol]
                if found:
                    found_symbols.append({
                        'symbol': symbol,
                        'instrument_token': found[0]['instrument_token'],
                        'exchange': found[0]['exchange']
                    })
            
            return {
                'status': 'SUCCESS',
                'profile': profile,
                'total_instruments': len(instruments),
                'found_symbols': found_symbols,
                'found_count': len(found_symbols)
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    def get_market_session(self) -> str:
        """Get current market session."""
        now = datetime.now()
        current_time = now.time()
        
        # Indian market timings
        pre_market_start = time(9, 0)   # 9:00 AM
        market_open = time(9, 15)       # 9:15 AM
        market_close = time(15, 30)     # 3:30 PM
        post_market_end = time(16, 0)   # 4:00 PM
        
        if current_time < pre_market_start:
            return "closed"
        elif pre_market_start <= current_time < market_open:
            return "pre_market"
        elif market_open <= current_time < market_close:
            return "live_market"
        elif market_close <= current_time < post_market_end:
            return "post_market"
        else:
            return "closed"

def display_debug_tab(kite: Optional[KiteConnect] = None):
    """Display debug information in Streamlit."""
    st.markdown("### 🔧 Debug: Stock Data Fetching")
    
    # Initialize debug fetcher
    debug_fetcher = DebugStockDataFetcher(kite)
    
    # Current time and market session
    current_time = datetime.now()
    market_session = debug_fetcher.get_market_session()
    
    st.markdown(f"**🕐 Current Time:** {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**📈 Market Session:** {market_session}")
    
    # Test buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Test Yahoo Finance"):
            st.markdown("---")
            st.markdown("#### Yahoo Finance Test Results")
            
            results_df = debug_fetcher.test_all_yahoo_finance()
            
            # Display results
            st.dataframe(results_df, use_container_width=True)
            
            # Summary
            success_count = len(results_df[results_df['status'] == 'SUCCESS'])
            volume_meets_criteria = len(results_df[results_df.get('meets_volume_criteria', False) == True])
            
            st.markdown(f"**✅ Successful fetches:** {success_count}/{len(results_df)}")
            st.markdown(f"**📊 Stocks meeting volume criteria (>75K):** {volume_meets_criteria}")
            
            # Show errors if any
            errors = results_df[results_df['status'] != 'SUCCESS']
            if not errors.empty:
                st.markdown("#### ❌ Errors:")
                for _, error in errors.iterrows():
                    st.error(f"**{error['symbol']}:** {error.get('error', 'Unknown error')}")
    
    with col2:
        if st.button("🔗 Test Kite Connection"):
            st.markdown("---")
            st.markdown("#### Kite API Test Results")
            
            kite_test = debug_fetcher.test_kite_connection()
            
            if kite_test['status'] == 'NO_KITE':
                st.warning("⚠️ No Kite connection available. Please login first.")
            elif kite_test['status'] == 'SUCCESS':
                st.success("✅ Kite connection successful!")
                st.markdown(f"**User:** {kite_test['profile'].get('user_name', 'Unknown')}")
                st.markdown(f"**Total Instruments:** {kite_test['total_instruments']:,}")
                st.markdown(f"**Found Test Symbols:** {kite_test['found_count']}/{len(debug_fetcher.test_symbols)}")
                
                if kite_test['found_symbols']:
                    st.markdown("#### Found Symbols:")
                    for symbol_info in kite_test['found_symbols']:
                        st.markdown(f"- **{symbol_info['symbol']}**: Token {symbol_info['instrument_token']}")
            else:
                st.error("❌ Kite connection failed!")
                st.error(kite_test.get('error', 'Unknown error'))
    
    with col3:
        if st.button("🔄 Test Both Sources"):
            st.markdown("---")
            st.markdown("#### Comprehensive Test")
            
            # Test Yahoo Finance
            st.markdown("##### Yahoo Finance Results:")
            yf_results = debug_fetcher.test_all_yahoo_finance()
            yf_success = len(yf_results[yf_results['status'] == 'SUCCESS'])
            st.markdown(f"✅ Yahoo Finance: {yf_success}/{len(yf_results)} successful")
            
            # Test Kite
            st.markdown("##### Kite API Results:")
            kite_test = debug_fetcher.test_kite_connection()
            if kite_test['status'] == 'SUCCESS':
                st.markdown(f"✅ Kite API: Connected ({kite_test['found_count']} symbols found)")
            else:
                st.markdown(f"❌ Kite API: {kite_test['status']}")
            
            # Recommendation
            st.markdown("##### 💡 Recommendation:")
            if yf_success > 0:
                st.success("Yahoo Finance is working. The issue might be with volume filtering or data processing.")
            else:
                st.error("Yahoo Finance is not working. This could be due to network issues or API changes.")
    
    # Manual test section
    st.markdown("---")
    st.markdown("#### 🎯 Manual Single Stock Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_symbol = st.selectbox("Select a stock to test:", debug_fetcher.test_symbols)
    
    with col2:
        if st.button("🧪 Test Single Stock"):
            if test_symbol:
                st.markdown(f"##### Testing {test_symbol}:")
                result = debug_fetcher.test_yahoo_finance_single_stock(test_symbol)
                
                if result['status'] == 'SUCCESS':
                    st.success(f"✅ Successfully fetched data for {test_symbol}")
                    st.json(result)
                else:
                    st.error(f"❌ Failed to fetch data for {test_symbol}")
                    st.error(result.get('error', 'Unknown error'))
    
    # Current market data display
    st.markdown("---")
    st.markdown("#### 📊 Current Market Data (if available)")
    
    if st.button("📈 Show Available Data"):
        try:
            # Try to get data using the original method
            from nifty500_high_volume_stock_screener import MarketDataFetcher
            
            original_fetcher = MarketDataFetcher(kite)
            df = original_fetcher.get_high_volume_stocks()
            
            if df.empty:
                st.warning("⚠️ No data available from the original fetcher. This confirms the issue.")
                
                # Try with reduced volume threshold for testing
                original_fetcher.min_volume = 1000  # Reduce to 1K for testing
                df_reduced = original_fetcher.get_high_volume_stocks()
                
                if not df_reduced.empty:
                    st.info(f"📊 Found {len(df_reduced)} stocks with volume > 1,000")
                    st.dataframe(df_reduced.head(10))
                else:
                    st.error("❌ No stocks found even with reduced volume threshold.")
            else:
                st.success(f"✅ Found {len(df)} stocks meeting criteria!")
                st.dataframe(df.head(10))
                
        except Exception as e:
            st.error(f"❌ Error testing original fetcher: {str(e)}")
            st.error(traceback.format_exc())
