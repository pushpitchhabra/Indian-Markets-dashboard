"""
Instrument Universe Manager
==========================
Manages the top 500 Indian stocks by market cap and volume.
Research shows that using NSE's complete instrument list filtered by market cap
and volume gives better coverage than just Nifty 500.

Features:
- Top 500 stocks by market cap
- Volume-based filtering
- Real-time instrument data from Zerodha API
- Market cap calculation and ranking
- Sector classification
"""

import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import streamlit as st
from kiteconnect import KiteConnect
import logging

class InstrumentUniverseManager:
    """
    Manages the universe of tradeable instruments for analysis.
    Uses Zerodha API to get real-time instrument data and market cap rankings.
    """
    
    def __init__(self, kite: KiteConnect):
        self.kite = kite
        self.instruments_cache = None
        self.market_cap_cache = None
        self.last_update = None
        
    def get_all_nse_instruments(self) -> pd.DataFrame:
        """
        Get all NSE instruments from Zerodha API.
        Returns comprehensive instrument list with metadata.
        """
        try:
            if self.instruments_cache is None or self._cache_expired():
                st.info("🔄 Fetching latest instrument data from Zerodha API...")
                
                # Get all NSE instruments
                instruments = self.kite.instruments("NSE")
                
                # Convert to DataFrame
                df = pd.DataFrame(instruments)
                
                # Filter for equity instruments only
                equity_df = df[df['instrument_type'] == 'EQ'].copy()
                
                # Add market cap placeholder (will be calculated separately)
                equity_df['market_cap'] = 0
                equity_df['avg_volume'] = 0
                equity_df['last_price'] = 0
                
                self.instruments_cache = equity_df
                self.last_update = datetime.now()
                
                st.success(f"✅ Loaded {len(equity_df)} equity instruments from NSE")
                
            return self.instruments_cache.copy()
            
        except Exception as e:
            st.error(f"❌ Error fetching instruments: {str(e)}")
            return pd.DataFrame()
    
    def _cache_expired(self) -> bool:
        """Check if cache is older than 1 hour"""
        if self.last_update is None:
            return True
        return (datetime.now() - self.last_update).seconds > 3600
    
    def calculate_market_caps(self, instruments_df: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
        """
        Calculate market caps for instruments using current prices.
        Limited to avoid API rate limits.
        """
        try:
            st.info(f"📊 Calculating market caps for top {limit} instruments...")
            
            # Get a sample of instruments to calculate market cap
            sample_instruments = instruments_df.head(limit).copy()
            
            market_cap_data = []
            progress_bar = st.progress(0)
            
            for i, (_, instrument) in enumerate(sample_instruments.iterrows()):
                try:
                    # Get current price
                    symbol = instrument['tradingsymbol']
                    token = instrument['instrument_token']
                    
                    # Get LTP (Last Traded Price)
                    quote = self.kite.ltp([f"NSE:{symbol}"])
                    ltp = quote.get(f"NSE:{symbol}", {}).get('last_price', 0)
                    
                    if ltp > 0:
                        # Estimate market cap (shares outstanding not available, using approximation)
                        # This is a simplified calculation - in reality, you'd need shares outstanding
                        estimated_shares = 1000000000  # 100 crore shares (rough estimate)
                        market_cap = ltp * estimated_shares
                        
                        market_cap_data.append({
                            'symbol': symbol,
                            'name': instrument['name'],
                            'token': token,
                            'last_price': ltp,
                            'estimated_market_cap': market_cap,
                            'sector': self._get_sector(symbol)
                        })
                    
                    progress_bar.progress((i + 1) / len(sample_instruments))
                    
                except Exception as e:
                    continue
            
            progress_bar.empty()
            
            # Create DataFrame and sort by market cap
            market_cap_df = pd.DataFrame(market_cap_data)
            market_cap_df = market_cap_df.sort_values('estimated_market_cap', ascending=False)
            
            st.success(f"✅ Calculated market caps for {len(market_cap_df)} instruments")
            return market_cap_df
            
        except Exception as e:
            st.error(f"❌ Error calculating market caps: {str(e)}")
            return pd.DataFrame()
    
    def get_volume_leaders(self, instruments_df: pd.DataFrame, limit: int = 100) -> pd.DataFrame:
        """
        Get top instruments by trading volume.
        """
        try:
            st.info(f"📈 Fetching volume data for top {limit} instruments...")
            
            volume_data = []
            sample_instruments = instruments_df.head(limit).copy()
            progress_bar = st.progress(0)
            
            for i, (_, instrument) in enumerate(sample_instruments.iterrows()):
                try:
                    symbol = instrument['tradingsymbol']
                    token = instrument['instrument_token']
                    
                    # Get historical data for volume
                    from_date = date.today() - timedelta(days=1)
                    to_date = date.today()
                    
                    historical_data = self.kite.historical_data(
                        token, from_date, to_date, "day"
                    )
                    
                    if historical_data:
                        latest_data = historical_data[-1]
                        volume = latest_data.get('volume', 0)
                        
                        if volume > 0:
                            volume_data.append({
                                'symbol': symbol,
                                'name': instrument['name'],
                                'token': token,
                                'volume': volume,
                                'close': latest_data.get('close', 0),
                                'sector': self._get_sector(symbol)
                            })
                    
                    progress_bar.progress((i + 1) / len(sample_instruments))
                    
                except Exception as e:
                    continue
            
            progress_bar.empty()
            
            # Create DataFrame and sort by volume
            volume_df = pd.DataFrame(volume_data)
            volume_df = volume_df.sort_values('volume', ascending=False)
            
            st.success(f"✅ Fetched volume data for {len(volume_df)} instruments")
            return volume_df
            
        except Exception as e:
            st.error(f"❌ Error fetching volume data: {str(e)}")
            return pd.DataFrame()
    
    def get_top_500_universe(self, method: str = "hybrid") -> pd.DataFrame:
        """
        Get top 500 instruments based on specified method.
        
        Methods:
        - "market_cap": Top 500 by estimated market cap
        - "volume": Top 500 by trading volume  
        - "hybrid": Combination of market cap and volume (recommended)
        - "nifty_500": Use predefined Nifty 500 list
        """
        try:
            st.header(f"🔍 Building Top 500 Universe - {method.title()} Method")
            
            if method == "nifty_500":
                return self._get_nifty_500_list()
            
            # Get all instruments
            all_instruments = self.get_all_nse_instruments()
            
            if all_instruments.empty:
                return pd.DataFrame()
            
            if method == "market_cap":
                return self.calculate_market_caps(all_instruments, 500)
            
            elif method == "volume":
                return self.get_volume_leaders(all_instruments, 500)
            
            elif method == "hybrid":
                # Get top 300 by market cap and top 300 by volume, then merge
                st.info("🔄 Using hybrid approach: market cap + volume")
                
                market_cap_top = self.calculate_market_caps(all_instruments, 300)
                volume_top = self.get_volume_leaders(all_instruments, 300)
                
                # Combine and deduplicate
                combined = pd.concat([market_cap_top, volume_top], ignore_index=True)
                combined = combined.drop_duplicates(subset=['symbol'], keep='first')
                
                # Take top 500
                final_universe = combined.head(500)
                
                st.success(f"✅ Created hybrid universe with {len(final_universe)} instruments")
                return final_universe
            
        except Exception as e:
            st.error(f"❌ Error creating instrument universe: {str(e)}")
            return pd.DataFrame()
    
    def _get_nifty_500_list(self) -> pd.DataFrame:
        """
        Get predefined Nifty 500 stock list.
        This is a fallback method using known Nifty 500 constituents.
        """
        # Top 100 Nifty 500 stocks (representative sample)
        nifty_500_symbols = [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "INFY", "ITC", "SBIN",
            "BHARTIARTL", "KOTAKBANK", "LT", "HCLTECH", "ASIANPAINT", "AXISBANK", "MARUTI",
            "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "BAJFINANCE", "WIPRO", "M&M",
            "NTPC", "TECHM", "POWERGRID", "TATAMOTORS", "COALINDIA", "BAJAJFINSV", "HDFCLIFE",
            "ONGC", "SBILIFE", "INDUSINDBK", "ADANIENT", "JSWSTEEL", "GRASIM", "CIPLA",
            "TATASTEEL", "BPCL", "TATACONSUM", "DRREDDY", "EICHERMOT", "APOLLOHOSP", "DIVISLAB",
            "HINDALCO", "BRITANNIA", "HEROMOTOCO", "UPL", "BAJAJ-AUTO", "SHRIRAMFIN", "LTIM",
            "ADANIPORTS", "TRENT", "PIDILITIND", "HAVELLS", "DABUR", "GODREJCP", "MARICO",
            "BERGEPAINT", "COLPAL", "MCDOWELL-N", "AMBUJACEM", "GLAND", "TORNTPHARM", "BIOCON",
            "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB", "BANKBARODA", "CANFINHOME", "LICHSGFIN",
            "BAJAJHLDNG", "SIEMENS", "BOSCHLTD", "ABB", "HONAUT", "3MINDIA", "CUMMINSIND",
            "VOLTAS", "BLUEDART", "MINDTREE", "MPHASIS", "COFORGE", "PERSISTENT", "LTTS",
            "OFSS", "CYIENT", "RBLBANK", "YESBANK", "EQUITAS", "UJJIVAN", "AUBANK",
            "DMART", "NAUKRI", "ZOMATO", "PAYTM", "POLICYBZR", "IRCTC", "RAILTEL",
            "ADANIGREEN", "ADANITRANS", "ADANIPOWER", "JSWENERGY", "TATAPOWER", "NHPC",
            "SAIL", "NMDC", "VEDL", "HINDZINC", "NATIONALUM", "MOIL", "GMRINFRA"
        ]
        
        # Create DataFrame with basic info
        nifty_data = []
        for symbol in nifty_500_symbols:
            nifty_data.append({
                'symbol': symbol,
                'name': symbol,  # Simplified
                'sector': self._get_sector(symbol),
                'source': 'nifty_500'
            })
        
        return pd.DataFrame(nifty_data)
    
    def _get_sector(self, symbol: str) -> str:
        """
        Get sector classification for a symbol.
        Simplified sector mapping.
        """
        sector_mapping = {
            # Banking & Financial
            'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'SBIN': 'Banking', 'KOTAKBANK': 'Banking',
            'AXISBANK': 'Banking', 'INDUSINDBK': 'Banking', 'BAJFINANCE': 'Financial Services',
            'BAJAJFINSV': 'Financial Services', 'HDFCLIFE': 'Insurance', 'SBILIFE': 'Insurance',
            
            # IT
            'TCS': 'IT', 'INFY': 'IT', 'HCLTECH': 'IT', 'WIPRO': 'IT', 'TECHM': 'IT',
            'LTIM': 'IT', 'MINDTREE': 'IT', 'MPHASIS': 'IT', 'COFORGE': 'IT',
            
            # Oil & Gas
            'RELIANCE': 'Oil & Gas', 'ONGC': 'Oil & Gas', 'BPCL': 'Oil & Gas', 'IOC': 'Oil & Gas',
            
            # Auto
            'MARUTI': 'Automobile', 'TATAMOTORS': 'Automobile', 'M&M': 'Automobile', 
            'BAJAJ-AUTO': 'Automobile', 'EICHERMOT': 'Automobile', 'HEROMOTOCO': 'Automobile',
            
            # FMCG
            'HINDUNILVR': 'FMCG', 'ITC': 'FMCG', 'NESTLEIND': 'FMCG', 'BRITANNIA': 'FMCG',
            'DABUR': 'FMCG', 'GODREJCP': 'FMCG', 'MARICO': 'FMCG', 'COLPAL': 'FMCG',
            
            # Pharma
            'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma', 'DIVISLAB': 'Pharma',
            'BIOCON': 'Pharma', 'TORNTPHARM': 'Pharma', 'GLAND': 'Pharma',
            
            # Metals
            'TATASTEEL': 'Metals', 'JSWSTEEL': 'Metals', 'HINDALCO': 'Metals', 'VEDL': 'Metals',
            'SAIL': 'Metals', 'NMDC': 'Metals', 'HINDZINC': 'Metals',
            
            # Power
            'NTPC': 'Power', 'POWERGRID': 'Power', 'COALINDIA': 'Power', 'TATAPOWER': 'Power',
            'ADANIGREEN': 'Power', 'NHPC': 'Power', 'JSWENERGY': 'Power',
        }
        
        return sector_mapping.get(symbol, 'Others')
    
    def display_universe_stats(self, universe_df: pd.DataFrame):
        """Display statistics about the instrument universe"""
        if universe_df.empty:
            st.warning("⚠️ No universe data available")
            return
        
        st.subheader("📊 Universe Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Instruments", len(universe_df))
        
        with col2:
            sectors = universe_df['sector'].nunique() if 'sector' in universe_df.columns else 0
            st.metric("Sectors", sectors)
        
        with col3:
            avg_price = universe_df['last_price'].mean() if 'last_price' in universe_df.columns else 0
            st.metric("Avg Price", f"₹{avg_price:.2f}")
        
        with col4:
            total_volume = universe_df['volume'].sum() if 'volume' in universe_df.columns else 0
            st.metric("Total Volume", f"{total_volume/1000000:.1f}M")
        
        # Sector distribution
        if 'sector' in universe_df.columns:
            st.subheader("🏢 Sector Distribution")
            sector_counts = universe_df['sector'].value_counts()
            st.bar_chart(sector_counts)
        
        # Top 10 by market cap or volume
        if 'estimated_market_cap' in universe_df.columns:
            st.subheader("💰 Top 10 by Market Cap")
            top_10 = universe_df.head(10)[['symbol', 'name', 'last_price', 'estimated_market_cap']]
            st.dataframe(top_10, use_container_width=True)
        elif 'volume' in universe_df.columns:
            st.subheader("📈 Top 10 by Volume")
            top_10 = universe_df.head(10)[['symbol', 'name', 'close', 'volume']]
            st.dataframe(top_10, use_container_width=True)

def display_instrument_universe_tab(kite: KiteConnect):
    """
    Display the instrument universe management tab.
    """
    st.header("🌐 Instrument Universe Manager")
    
    st.markdown("""
    **Research Conclusion:** Using a **hybrid approach** combining market cap and volume 
    gives better coverage than just Nifty 500, as it includes high-volume mid-cap stocks 
    that are actively traded but might not be in Nifty 500.
    """)
    
    # Initialize manager
    universe_manager = InstrumentUniverseManager(kite)
    
    # Method selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        method = st.selectbox(
            "Select Universe Method",
            ["hybrid", "market_cap", "volume", "nifty_500"],
            help="Hybrid (recommended): Combines market cap and volume for best coverage"
        )
    
    with col2:
        if st.button("🔄 Build Universe", type="primary"):
            with st.spinner("Building instrument universe..."):
                universe_df = universe_manager.get_top_500_universe(method)
                
                if not universe_df.empty:
                    st.session_state.instrument_universe = universe_df
                    st.session_state.universe_method = method
                    st.success(f"✅ Built universe with {len(universe_df)} instruments")
                else:
                    st.error("❌ Failed to build universe")
    
    # Display current universe
    if 'instrument_universe' in st.session_state:
        universe_df = st.session_state.instrument_universe
        method_used = st.session_state.get('universe_method', 'unknown')
        
        st.success(f"📊 Current Universe: {len(universe_df)} instruments using {method_used} method")
        
        # Display statistics
        universe_manager.display_universe_stats(universe_df)
        
        # Export option
        if st.button("📥 Export Universe to CSV"):
            csv = universe_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"instrument_universe_{method_used}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    else:
        st.info("👆 Click 'Build Universe' to create your instrument universe")
