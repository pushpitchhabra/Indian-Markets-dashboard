import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
# Removed yfinance - using only Zerodha API
import requests
from typing import List, Dict, Optional, Tuple
import streamlit as st
from kiteconnect import KiteConnect
import time as time_module
import json

class MarketDataFetcher:
    """
    A comprehensive module to fetch pre-market, live market, and post-market data
    for Nifty 500 stocks with volume filtering capabilities.
    """
    
    def __init__(self, kite: Optional[KiteConnect] = None):
        self.kite = kite
        self.min_volume = 75000
        self.nifty_500_symbols = self._get_nifty_500_symbols()
        
    def _get_nifty_500_symbols(self) -> List[str]:
        """
        Get list of Nifty 500 stock symbols.
        This is a comprehensive list of major Indian stocks.
        """
        # Major Nifty 500 stocks - in a real implementation, you'd fetch this from NSE
        nifty_500_stocks = [
            # Top 50 stocks from Nifty 500
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
            "ZOMATO", "NYKAA", "PAYTM", "POLICYBZR", "STAR", "ZEEL", "SUNTV",
            "NETWORK18", "TV18BRDCST", "HATHWAY", "DEN", "GTPL", "SITICABLE",
            "RCOM", "IDEA", "BSNL", "MTNL", "TTML", "RAILTEL", "ITI", "HFCL",
            "STERLITE", "TEJAS", "ROUTE", "OPTIEMUS", "DIXON", "AMBER", "NELCO",
            "REDINGTON", "RASHI", "SUPERTEX", "TEXRAIL", "WELCORP", "WELSPUN",
            "GARWARE", "FILATEX", "TRIDENT", "VARDHMAN", "ARVIND", "RAYMOND",
            "VIPIND", "PENINLAND", "CENTURY", "CENTURYTEX", "ALOKTEXT", "RSWM"
        ]
        
        return nifty_500_stocks[:100]  # Using top 100 for demo
    
    def get_market_session(self) -> str:
        """
        Determine current market session based on Indian market timings.
        """
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
    
    def fetch_stock_data_yfinance(self, symbols: List[str]) -> pd.DataFrame:
        """
        DEPRECATED: yfinance fallback removed - using Zerodha API only.
        """
        stock_data = []
        
        for symbol in symbols:
            try:
                # Add .NS suffix for NSE stocks
                ticker = f"{symbol}.NS"
                stock = yf.Ticker(ticker)
                
                # Get current data
                info = stock.info
                hist = stock.history(period="1d", interval="1m")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].sum()  # Total volume for the day
                    
                    # Calculate price change
                    if len(hist) > 1:
                        prev_close = info.get('previousClose', hist['Close'].iloc[0])
                        price_change = current_price - prev_close
                        price_change_pct = (price_change / prev_close) * 100
                    else:
                        price_change = 0
                        price_change_pct = 0
                    
                    stock_data.append({
                        'symbol': symbol,
                        'current_price': round(current_price, 2),
                        'volume': int(volume),
                        'price_change': round(price_change, 2),
                        'price_change_pct': round(price_change_pct, 2),
                        'high': round(hist['High'].max(), 2),
                        'low': round(hist['Low'].min(), 2),
                        'market_cap': info.get('marketCap', 0),
                        'last_updated': datetime.now().strftime('%H:%M:%S')
                    })
                    
            except Exception as e:
                print(f"Error fetching data for {symbol}: {str(e)}")
                continue
        
        return pd.DataFrame(stock_data)
    
    def fetch_stock_data_kite(self, symbols: List[str]) -> pd.DataFrame:
        """
        Fetch stock data using Kite Connect API (primary method).
        """
        if not self.kite:
            return pd.DataFrame()
        
        stock_data = []
        
        try:
            # Get instrument tokens for symbols
            instruments = self.kite.instruments("NSE")
            symbol_token_map = {inst['tradingsymbol']: inst['instrument_token'] 
                              for inst in instruments 
                              if inst['tradingsymbol'] in symbols}
            
            # Fetch quotes for all symbols
            tokens = list(symbol_token_map.values())
            if tokens:
                quotes = self.kite.quote(tokens)
                
                for symbol in symbols:
                    token = symbol_token_map.get(symbol)
                    if token and token in quotes:
                        quote = quotes[token]
                        
                        volume = quote.get('volume', 0)
                        if volume >= self.min_volume:
                            stock_data.append({
                                'symbol': symbol,
                                'current_price': quote.get('last_price', 0),
                                'volume': volume,
                                'price_change': quote.get('net_change', 0),
                                'price_change_pct': quote.get('net_change', 0) / quote.get('last_price', 1) * 100,
                                'high': quote.get('ohlc', {}).get('high', 0),
                                'low': quote.get('ohlc', {}).get('low', 0),
                                'open': quote.get('ohlc', {}).get('open', 0),
                                'close': quote.get('ohlc', {}).get('close', 0),
                                'last_updated': datetime.now().strftime('%H:%M:%S')
                            })
                            
        except Exception as e:
            print(f"Error fetching data from Kite: {str(e)}")
            return pd.DataFrame()
        
        return pd.DataFrame(stock_data)
    
    def get_high_volume_stocks(self, session_type: str = None) -> pd.DataFrame:
        """
        Get high volume stocks based on current market session.
        """
        if session_type is None:
            session_type = self.get_market_session()
        
        # Use Kite API only - no fallback
        try:
            df = self.fetch_stock_data_kite(self.nifty_500_symbols)
        except Exception as e:
            st.error(f"Failed to fetch data from Zerodha API: {e}")
            return pd.DataFrame()
        
        if df.empty:
            return df
        
        # Filter by minimum volume
        df = df[df['volume'] >= self.min_volume]
        
        # Sort by volume (highest first)
        df = df.sort_values('volume', ascending=False)
        
        # Add session information
        df['market_session'] = session_type
        
        return df.reset_index(drop=True)
    
    def get_market_movers(self, move_type: str = "gainers") -> pd.DataFrame:
        """
        Get top gainers or losers from high volume stocks.
        """
        df = self.get_high_volume_stocks()
        
        if df.empty:
            return df
        
        if move_type == "gainers":
            return df[df['price_change_pct'] > 0].sort_values('price_change_pct', ascending=False).head(20)
        elif move_type == "losers":
            return df[df['price_change_pct'] < 0].sort_values('price_change_pct', ascending=True).head(20)
        else:
            return df.head(20)
    
    def get_volume_leaders(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get stocks with highest trading volume.
        """
        df = self.get_high_volume_stocks()
        return df.head(top_n) if not df.empty else df
    
    def format_volume(self, volume: int) -> str:
        """
        Format volume in readable format (K, L, Cr).
        """
        if volume >= 10000000:  # 1 Crore
            return f"{volume/10000000:.1f}Cr"
        elif volume >= 100000:  # 1 Lakh
            return f"{volume/100000:.1f}L"
        elif volume >= 1000:  # 1 Thousand
            return f"{volume/1000:.1f}K"
        else:
            return str(volume)
    
    def get_market_summary(self) -> Dict:
        """
        Get overall market summary.
        """
        df = self.get_high_volume_stocks()
        
        if df.empty:
            return {
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'unchanged': 0,
                'total_volume': 0,
                'avg_change': 0
            }
        
        return {
            'total_stocks': len(df),
            'gainers': len(df[df['price_change_pct'] > 0]),
            'losers': len(df[df['price_change_pct'] < 0]),
            'unchanged': len(df[df['price_change_pct'] == 0]),
            'total_volume': df['volume'].sum(),
            'avg_change': df['price_change_pct'].mean(),
            'session': self.get_market_session()
        }

# Streamlit UI Integration Functions
def display_market_data_tab(kite: Optional[KiteConnect] = None):
    """
    Display market data in Streamlit interface.
    """
    st.markdown("### 📈 Live Market Data & High Volume Stocks")
    
    # Initialize market data fetcher
    fetcher = MarketDataFetcher(kite)
    
    # Market session indicator
    session = fetcher.get_market_session()
    session_colors = {
        'pre_market': '🟡',
        'live_market': '🟢',
        'post_market': '🟠',
        'closed': '🔴'
    }
    
    st.markdown(f"**Market Status:** {session_colors.get(session, '⚪')} {session.replace('_', ' ').title()}")
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        auto_refresh = st.checkbox("Auto Refresh", value=False)
    
    with col2:
        refresh_interval = st.selectbox("Refresh Interval", [30, 60, 120, 300], index=1)
    
    with col3:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Auto refresh logic
    if auto_refresh:
        time_module.sleep(refresh_interval)
        st.rerun()
    
    # Market Summary
    summary = fetcher.get_market_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Stocks", summary['total_stocks'])
    
    with col2:
        st.metric("Gainers", summary['gainers'], delta=f"+{summary['gainers']}")
    
    with col3:
        st.metric("Losers", summary['losers'], delta=f"-{summary['losers']}")
    
    with col4:
        st.metric("Avg Change %", f"{summary['avg_change']:.2f}%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Volume Leaders", "📈 Top Gainers", "📉 Top Losers", "📊 All Stocks"])
    
    with tab1:
        st.markdown("#### Stocks with Highest Trading Volume (>75K)")
        volume_leaders = fetcher.get_volume_leaders(20)
        
        if not volume_leaders.empty:
            # Format the dataframe for display
            display_df = volume_leaders.copy()
            display_df['volume_formatted'] = display_df['volume'].apply(fetcher.format_volume)
            display_df['price_change_formatted'] = display_df.apply(
                lambda x: f"₹{x['price_change']:+.2f} ({x['price_change_pct']:+.2f}%)", axis=1
            )
            
            st.dataframe(
                display_df[['symbol', 'current_price', 'volume_formatted', 'price_change_formatted', 'high', 'low', 'last_updated']],
                column_config={
                    'symbol': 'Symbol',
                    'current_price': st.column_config.NumberColumn('Price (₹)', format="₹%.2f"),
                    'volume_formatted': 'Volume',
                    'price_change_formatted': 'Change',
                    'high': st.column_config.NumberColumn('High (₹)', format="₹%.2f"),
                    'low': st.column_config.NumberColumn('Low (₹)', format="₹%.2f"),
                    'last_updated': 'Updated'
                },
                use_container_width=True
            )
        else:
            st.info("No high volume stocks found at the moment.")
    
    with tab2:
        st.markdown("#### Top Gainers (High Volume)")
        gainers = fetcher.get_market_movers("gainers")
        
        if not gainers.empty:
            display_df = gainers.copy()
            display_df['volume_formatted'] = display_df['volume'].apply(fetcher.format_volume)
            
            st.dataframe(
                display_df[['symbol', 'current_price', 'price_change_pct', 'volume_formatted', 'last_updated']],
                column_config={
                    'symbol': 'Symbol',
                    'current_price': st.column_config.NumberColumn('Price (₹)', format="₹%.2f"),
                    'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                    'volume_formatted': 'Volume',
                    'last_updated': 'Updated'
                },
                use_container_width=True
            )
        else:
            st.info("No gainers found in high volume stocks.")
    
    with tab3:
        st.markdown("#### Top Losers (High Volume)")
        losers = fetcher.get_market_movers("losers")
        
        if not losers.empty:
            display_df = losers.copy()
            display_df['volume_formatted'] = display_df['volume'].apply(fetcher.format_volume)
            
            st.dataframe(
                display_df[['symbol', 'current_price', 'price_change_pct', 'volume_formatted', 'last_updated']],
                column_config={
                    'symbol': 'Symbol',
                    'current_price': st.column_config.NumberColumn('Price (₹)', format="₹%.2f"),
                    'price_change_pct': st.column_config.NumberColumn('Change %', format="%.2f%%"),
                    'volume_formatted': 'Volume',
                    'last_updated': 'Updated'
                },
                use_container_width=True
            )
        else:
            st.info("No losers found in high volume stocks.")
    
    with tab4:
        st.markdown("#### All High Volume Stocks")
        all_stocks = fetcher.get_high_volume_stocks()
        
        if not all_stocks.empty:
            display_df = all_stocks.copy()
            display_df['volume_formatted'] = display_df['volume'].apply(fetcher.format_volume)
            display_df['price_change_formatted'] = display_df.apply(
                lambda x: f"₹{x['price_change']:+.2f} ({x['price_change_pct']:+.2f}%)", axis=1
            )
            
            st.dataframe(
                display_df[['symbol', 'current_price', 'volume_formatted', 'price_change_formatted', 'high', 'low', 'last_updated']],
                column_config={
                    'symbol': 'Symbol',
                    'current_price': st.column_config.NumberColumn('Price (₹)', format="₹%.2f"),
                    'volume_formatted': 'Volume',
                    'price_change_formatted': 'Change',
                    'high': st.column_config.NumberColumn('High (₹)', format="₹%.2f"),
                    'low': st.column_config.NumberColumn('Low (₹)', format="₹%.2f"),
                    'last_updated': 'Updated'
                },
                use_container_width=True
            )
        else:
            st.info("No stocks meet the volume criteria (>75,000) at the moment.")
    
    # Market session info
    st.markdown("---")
    st.markdown(f"**📊 Data Source:** {'Zerodha Kite API' if kite else 'Yahoo Finance'}")
    st.markdown(f"**⏰ Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**📈 Market Session:** {session.replace('_', ' ').title()}")
    
    if session == 'closed':
        st.info("🕐 Market is currently closed. Data shown is from the last trading session.")
    elif session == 'pre_market':
        st.info("🌅 Pre-market session is active. Limited trading activity.")
    elif session == 'post_market':
        st.info("🌆 Post-market session is active. Limited trading activity.")
