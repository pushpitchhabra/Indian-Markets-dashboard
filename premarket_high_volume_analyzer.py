"""
Pre-Market High Volume Stock Analyzer
=====================================
Specialized module for pre-market analysis focusing on stocks with highest trading 
activity from the last trading day. Designed specifically for pre-market preparation 
and analysis, separate from live market models.

Features:
- Last trading day high-volume stock identification
- Pre-market preparation data and insights
- Historical volume analysis for pre-market planning
- Date selection for custom pre-market analysis
- Volume leaders from previous trading sessions

Author: AI Assistant for Indian Stock Market Pre-Market Analysis
Created: 2025-01-27
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta, time
# Removed yfinance - using only Zerodha API
import streamlit as st
from kiteconnect import KiteConnect
from typing import List, Dict, Optional, Tuple
import calendar
import traceback

class PreMarketHighVolumeAnalyzer:
    """
    Specialized analyzer for pre-market high-volume stock analysis.
    Focuses on identifying stocks with highest trading activity from previous sessions
    to help with pre-market preparation and planning.
    """
    
    def __init__(self, kite: Optional[KiteConnect] = None):
        self.kite = kite
        self.min_volume = 75000
        self.nifty_500_symbols = self._get_premarket_focus_symbols()
        
    def _get_premarket_focus_symbols(self) -> List[str]:
        """
        Get list of stocks most relevant for pre-market analysis.
        Focus on high-liquidity, actively traded stocks.
        """
        return [
            # High-liquidity stocks most active in pre-market
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", 
            "BHARTIARTL", "ITC", "SBIN", "LT", "ASIANPAINT", "AXISBANK",
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
        Get the last trading day for pre-market analysis.
        Excludes weekends and major Indian market holidays.
        """
        if from_date is None:
            from_date = date.today()
        
        # Major Indian market holidays 2025
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
            # Skip weekends
            if current_date.weekday() >= 5:
                current_date -= timedelta(days=1)
                continue
            
            # Skip holidays
            if current_date in indian_holidays_2025:
                current_date -= timedelta(days=1)
                continue
            
            # Safety check - don't go back more than 10 days
            if (from_date - current_date).days > 10:
                break
                
            return current_date
        
        return current_date
    
    def get_market_session(self) -> str:
        """
        Determine current market session based on Indian market timings.
        Returns: 'pre_market', 'live_market', 'post_market', or 'closed'
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
    
    def is_premarket_session(self) -> bool:
        """Check if current time is pre-market session (9:00 AM - 9:15 AM)."""
        return self.get_market_session() == "pre_market"
    
    def fetch_premarket_data_kite(self, symbols: List[str], target_date: date) -> pd.DataFrame:
        """
        Fetch pre-market relevant data using Kite API for a specific date.
        Focus on volume and price action data useful for pre-market analysis.
        """
        if not self.kite:
            return pd.DataFrame()
        
        stock_data = []
        
        try:
            instruments = self.kite.instruments("NSE")
            symbol_token_map = {inst['tradingsymbol']: inst['instrument_token'] 
                              for inst in instruments 
                              if inst['tradingsymbol'] in symbols}
            
            for symbol in symbols:
                token = symbol_token_map.get(symbol)
                if not token:
                    continue
                
                try:
                    historical_data = self.kite.historical_data(
                        instrument_token=token,
                        from_date=target_date,
                        to_date=target_date,
                        interval="day"
                    )
                    
                    if historical_data:
                        data = historical_data[0]
                        volume = data.get('volume', 0)
                        
                        if volume >= self.min_volume:
                            open_price = data.get('open', 0)
                            close_price = data.get('close', 0)
                            high_price = data.get('high', 0)
                            low_price = data.get('low', 0)
                            
                            # Calculate metrics important for pre-market analysis
                            price_change = close_price - open_price
                            price_change_pct = (price_change / open_price * 100) if open_price > 0 else 0
                            volatility = ((high_price - low_price) / open_price * 100) if open_price > 0 else 0
                            
                            stock_data.append({
                                'symbol': symbol,
                                'close_price': close_price,
                                'volume': volume,
                                'price_change': price_change,
                                'price_change_pct': price_change_pct,
                                'volatility_pct': volatility,
                                'high': high_price,
                                'low': low_price,
                                'open': open_price,
                                'date': target_date.strftime('%Y-%m-%d'),
                                'volume_category': self._categorize_volume(volume),
                                'premarket_score': self._calculate_premarket_score(volume, abs(price_change_pct), volatility),
                                'last_updated': datetime.now().strftime('%H:%M:%S')
                            })
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            st.error(f"Error fetching pre-market data from Kite: {str(e)}")
            return pd.DataFrame()
        
        return pd.DataFrame(stock_data)
    
    def fetch_premarket_data_yfinance(self, symbols: List[str], target_date: date) -> pd.DataFrame:
        """
        Fetch pre-market relevant data using Yahoo Finance for a specific date.
        Enhanced for pre-market analysis requirements.
        """
        stock_data = []
        
        start_date = target_date - timedelta(days=5)
        end_date = target_date + timedelta(days=1)
        
        for symbol in symbols:
            try:
                ticker = f"{symbol}.NS"
                stock = yf.Ticker(ticker)
                
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    continue
                
                # Find target date data
                target_data = None
                target_date_str = target_date.strftime('%Y-%m-%d')
                
                for idx in hist.index:
                    if idx.strftime('%Y-%m-%d') == target_date_str:
                        target_data = hist.loc[idx]
                        break
                
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
                        volatility = ((high_price - low_price) / open_price * 100) if open_price > 0 else 0
                        
                        stock_data.append({
                            'symbol': symbol,
                            'close_price': round(close_price, 2),
                            'volume': volume,
                            'price_change': round(price_change, 2),
                            'price_change_pct': round(price_change_pct, 2),
                            'volatility_pct': round(volatility, 2),
                            'high': round(high_price, 2),
                            'low': round(low_price, 2),
                            'open': round(open_price, 2),
                            'date': actual_date,
                            'volume_category': self._categorize_volume(volume),
                            'premarket_score': self._calculate_premarket_score(volume, abs(price_change_pct), volatility),
                            'last_updated': datetime.now().strftime('%H:%M:%S')
                        })
                        
            except Exception as e:
                continue
        
        return pd.DataFrame(stock_data)
    
    def _categorize_volume(self, volume: int) -> str:
        """Categorize volume for pre-market analysis."""
        if volume >= 5000000:  # 50L+
            return "Very High"
        elif volume >= 1000000:  # 10L+
            return "High"
        elif volume >= 500000:  # 5L+
            return "Medium"
        else:
            return "Low"
    
    def _calculate_premarket_score(self, volume: int, price_change_pct: float, volatility: float) -> float:
        """
        Calculate a pre-market interest score based on volume, price movement, and volatility.
        Higher score indicates more interesting for pre-market analysis.
        """
        # Normalize volume (0-40 points)
        volume_score = min(40, (volume / 1000000) * 10)
        
        # Price movement score (0-30 points)
        price_score = min(30, abs(price_change_pct) * 3)
        
        # Volatility score (0-30 points)
        volatility_score = min(30, volatility * 2)
        
        return round(volume_score + price_score + volatility_score, 1)
    
    def get_premarket_high_volume_stocks(self, target_date: date = None) -> pd.DataFrame:
        """
        Get high volume stocks specifically for pre-market analysis.
        """
        if target_date is None:
            target_date = self.get_last_trading_day()
        
        # Try Kite API first, fallback to Yahoo Finance
        if self.kite:
            df = self.fetch_premarket_data_kite(self.nifty_500_symbols, target_date)
        else:
            # Use Kite API only - no yfinance fallback
            if self.kite:
                df = self.fetch_premarket_data_kite(self.nifty_500_symbols, target_date)
            else:
                st.error("Zerodha API session required for data fetching")
                return pd.DataFrame()
        
        if df.empty:
            return df
        
        # Sort by pre-market score (most interesting first)
        df = df.sort_values('premarket_score', ascending=False)
        
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
    
    def get_premarket_insights(self, df: pd.DataFrame) -> Dict:
        """Generate pre-market specific insights from the data."""
        if df.empty:
            return {}
        
        # Top movers by pre-market score
        top_scorer = df.iloc[0]
        
        # Volume analysis
        very_high_volume = len(df[df['volume_category'] == 'Very High'])
        high_volume = len(df[df['volume_category'] == 'High'])
        
        # Price movement analysis
        big_movers = len(df[abs(df['price_change_pct']) >= 3])  # 3%+ moves
        
        # Volatility analysis
        high_volatility = len(df[df['volatility_pct'] >= 5])  # 5%+ volatility
        
        return {
            'top_premarket_stock': top_scorer['symbol'],
            'top_score': top_scorer['premarket_score'],
            'very_high_volume_count': very_high_volume,
            'high_volume_count': high_volume,
            'big_movers_count': big_movers,
            'high_volatility_count': high_volatility,
            'total_stocks': len(df),
            'avg_volume': df['volume'].mean(),
            'avg_price_change': df['price_change_pct'].mean()
        }
