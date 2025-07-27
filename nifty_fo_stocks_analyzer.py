"""
Nifty F&O Stocks Analyzer
Comprehensive analysis module for Futures & Options eligible stocks
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
import math
from scipy.stats import norm
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
warnings.filterwarnings('ignore')

class NiftyFOStocksAnalyzer:
    """Analyzer for Nifty F&O eligible stocks with comprehensive analytics."""
    
    def __init__(self):
        # Top F&O eligible stocks with lot sizes and sector mapping
        self.fo_stocks = {
            # Large Cap Stocks
            "RELIANCE": {"name": "Reliance Industries", "lot_size": 250, "sector": "Energy"},
            "TCS": {"name": "Tata Consultancy Services", "lot_size": 150, "sector": "IT"},
            "HDFCBANK": {"name": "HDFC Bank", "lot_size": 550, "sector": "Banking"},
            "ICICIBANK": {"name": "ICICI Bank", "lot_size": 1375, "sector": "Banking"},
            "INFY": {"name": "Infosys", "lot_size": 300, "sector": "IT"},
            "HINDUNILVR": {"name": "Hindustan Unilever", "lot_size": 300, "sector": "FMCG"},
            "ITC": {"name": "ITC", "lot_size": 3200, "sector": "FMCG"},
            "SBIN": {"name": "State Bank of India", "lot_size": 1500, "sector": "Banking"},
            "BHARTIARTL": {"name": "Bharti Airtel", "lot_size": 1200, "sector": "Telecom"},
            "ASIANPAINT": {"name": "Asian Paints", "lot_size": 150, "sector": "Paints"},
            
            # Banking Stocks
            "AXISBANK": {"name": "Axis Bank", "lot_size": 1200, "sector": "Banking"},
            "KOTAKBANK": {"name": "Kotak Mahindra Bank", "lot_size": 400, "sector": "Banking"},
            "INDUSINDBK": {"name": "IndusInd Bank", "lot_size": 900, "sector": "Banking"},
            "HDFCLIFE": {"name": "HDFC Life Insurance", "lot_size": 700, "sector": "Insurance"},
            "SBILIFE": {"name": "SBI Life Insurance", "lot_size": 400, "sector": "Insurance"},
            
            # IT Stocks
            "HCLTECH": {"name": "HCL Technologies", "lot_size": 350, "sector": "IT"},
            "WIPRO": {"name": "Wipro", "lot_size": 1200, "sector": "IT"},
            "TECHM": {"name": "Tech Mahindra", "lot_size": 400, "sector": "IT"},
            "LTI": {"name": "L&T Infotech", "lot_size": 125, "sector": "IT"},
            
            # Auto Stocks
            "MARUTI": {"name": "Maruti Suzuki", "lot_size": 100, "sector": "Auto"},
            "TATAMOTORS": {"name": "Tata Motors", "lot_size": 1500, "sector": "Auto"},
            "M&M": {"name": "Mahindra & Mahindra", "lot_size": 300, "sector": "Auto"},
            "BAJAJ-AUTO": {"name": "Bajaj Auto", "lot_size": 125, "sector": "Auto"},
            "EICHERMOT": {"name": "Eicher Motors", "lot_size": 100, "sector": "Auto"},
            
            # Energy & Oil
            "ONGC": {"name": "Oil & Natural Gas Corp", "lot_size": 4800, "sector": "Energy"},
            "IOC": {"name": "Indian Oil Corp", "lot_size": 6300, "sector": "Energy"},
            "BPCL": {"name": "Bharat Petroleum", "lot_size": 1000, "sector": "Energy"},
            "NTPC": {"name": "NTPC", "lot_size": 2000, "sector": "Power"},
            
            # Pharma Stocks
            "SUNPHARMA": {"name": "Sun Pharmaceutical", "lot_size": 400, "sector": "Pharma"},
            "DRREDDY": {"name": "Dr. Reddy's Labs", "lot_size": 125, "sector": "Pharma"},
            "CIPLA": {"name": "Cipla", "lot_size": 700, "sector": "Pharma"},
            "DIVISLAB": {"name": "Divi's Laboratories", "lot_size": 125, "sector": "Pharma"},
            
            # Metals & Mining
            "TATASTEEL": {"name": "Tata Steel", "lot_size": 4000, "sector": "Metals"},
            "HINDALCO": {"name": "Hindalco Industries", "lot_size": 1000, "sector": "Metals"},
            "JSWSTEEL": {"name": "JSW Steel", "lot_size": 1000, "sector": "Metals"},
            "COALINDIA": {"name": "Coal India", "lot_size": 4000, "sector": "Mining"},
            
            # FMCG & Consumer
            "NESTLEIND": {"name": "Nestle India", "lot_size": 25, "sector": "FMCG"},
            "BRITANNIA": {"name": "Britannia Industries", "lot_size": 125, "sector": "FMCG"},
            "DABUR": {"name": "Dabur India", "lot_size": 900, "sector": "FMCG"},
            
            # Others
            "LT": {"name": "Larsen & Toubro", "lot_size": 300, "sector": "Construction"},
            "ULTRACEMCO": {"name": "UltraTech Cement", "lot_size": 100, "sector": "Cement"},
            "GRASIM": {"name": "Grasim Industries", "lot_size": 400, "sector": "Textiles"},
            "ADANIPORTS": {"name": "Adani Ports", "lot_size": 1200, "sector": "Infrastructure"},
        }
        
        # Index F&O contracts (using same symbols as market indices tracker)
        self.index_fo = {
            "NIFTY": {"name": "Nifty 50", "symbol": "^NSEI", "lot_size": 50},
            "BANKNIFTY": {"name": "Bank Nifty", "symbol": "^NSEBANK", "lot_size": 25},
            "NIFTYIT": {"name": "Nifty IT", "symbol": "^CNXIT", "lot_size": 40},
            "NIFTYAUTO": {"name": "Nifty Auto", "symbol": "^CNXAUTO", "lot_size": 75}
        }
    
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get stock data with reliable fetching."""
        try:
            # Try multiple ticker formats for better success rate
            ticker_formats = [f"{symbol}.NS", f"{symbol}.BO", symbol]
            
            for ticker_symbol in ticker_formats:
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    data = ticker.history(period=period)
                    
                    if not data.empty and len(data) > 50:  # Need sufficient data for F&O analysis
                        return data.dropna()
                        
                except Exception as e:
                    continue
           
            return pd.DataFrame()
            
        except Exception as e:
            return pd.DataFrame()
    
    def get_fo_stock_data(self, symbol: str, period: str = "1mo") -> pd.DataFrame:
        """Get OHLCV data for F&O stock."""
        try:
            return self.get_stock_data(symbol, period)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_historical_volatility(self, data: pd.DataFrame, window: int = 30) -> float:
        """Calculate historical volatility (annualized)."""
        try:
            if len(data) < window:
                return 0.0
            
            # Calculate daily returns
            returns = data['Close'].pct_change().dropna()
            
            # Calculate rolling volatility
            volatility = returns.rolling(window=window).std().iloc[-1]
            
            # Annualize (assuming 252 trading days)
            annual_volatility = volatility * np.sqrt(252) * 100
            
            return round(annual_volatility, 2) if not pd.isna(annual_volatility) else 0.0
        except:
            return 0.0
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        try:
            if len(data) < period:
                return 0.0
            
            high_low = data['High'] - data['Low']
            high_close = np.abs(data['High'] - data['Close'].shift())
            low_close = np.abs(data['Low'] - data['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean().iloc[-1]
            
            return round(atr, 2) if not pd.isna(atr) else 0.0
        except:
            return 0.0
    
    def analyze_fo_stock(self, symbol: str) -> Dict:
        """Comprehensive F&O analysis for a single stock."""
        try:
            if symbol not in self.fo_stocks:
                return {'status': 'error', 'error': 'Stock not in F&O list'}
            
            data = self.get_fo_stock_data(symbol)
            if data.empty:
                return {'status': 'error', 'error': 'No data available'}
            
            stock_info = self.fo_stocks[symbol]
            
            # Basic price data with proper error handling
            current_price = float(data['Close'].iloc[-1])
            previous_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
            price_change = current_price - previous_close
            price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
            
            # Volume with NaN handling
            try:
                volume = data['Volume'].iloc[-1]
                if pd.isna(volume) or volume <= 0:
                    volume = 0
                else:
                    volume = int(volume)
            except:
                volume = 0
            
            # 52-week high/low
            high_52w = float(data['High'].rolling(252).max().iloc[-1])
            low_52w = float(data['Low'].rolling(252).min().iloc[-1])
            
            # Volume analysis with proper NaN handling
            try:
                current_volume = data['Volume'].iloc[-1]
                if pd.isna(current_volume) or current_volume <= 0:
                    current_volume = 0
                else:
                    current_volume = int(current_volume)
                
                if len(data) >= 20:
                    avg_volume_20d = data['Volume'].tail(20).mean()
                    if pd.isna(avg_volume_20d) or avg_volume_20d <= 0:
                        avg_volume_20d = current_volume if current_volume > 0 else 1
                    else:
                        avg_volume_20d = int(avg_volume_20d)
                else:
                    avg_volume_20d = current_volume if current_volume > 0 else 1
                
                volume_ratio = current_volume / avg_volume_20d if avg_volume_20d > 0 else 1
            except Exception as e:
                current_volume = 0
                avg_volume_20d = 1
                volume_ratio = 1
            
            # ATR for volatility
            atr = self.calculate_atr(data)
            
            # Historical volatility
            hist_volatility = self.calculate_historical_volatility(data)
            
            # Support and resistance levels (simple)
            support = float(data['Low'].rolling(20).min().iloc[-1])
            resistance = float(data['High'].rolling(20).max().iloc[-1])
            
            # Lot value calculation
            lot_value = current_price * stock_info['lot_size']
            
            return {
                'status': 'success',
                'symbol': symbol,
                'name': stock_info['name'],
                'sector': stock_info['sector'],
                'current_price': round(current_price, 2),
                'price_change': round(price_change, 2),
                'price_change_percent': round(price_change_percent, 2),
                'volume': volume,
                'volume_ratio': round(volume_ratio, 2),
                'lot_size': stock_info['lot_size'],
                'lot_value': round(lot_value, 2),
                'high_52w': round(high_52w, 2),
                'low_52w': round(low_52w, 2),
                'atr': atr,
                'historical_volatility': hist_volatility,
                'support': round(support, 2),
                'resistance': round(resistance, 2),
                'trading_signal': self._generate_trading_signal(data, volume_ratio, hist_volatility)
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _generate_trading_signal(self, data: pd.DataFrame, volume_ratio: float, volatility: float) -> str:
        """Generate simple trading signal based on volume and volatility."""
        try:
            if volume_ratio > 2 and volatility > 25:
                return "HIGH_ACTIVITY"
            elif volume_ratio > 1.5:
                return "MODERATE_ACTIVITY"
            elif volume_ratio < 0.5:
                return "LOW_ACTIVITY"
            else:
                return "NORMAL"
        except:
            return "NORMAL"
    
    def get_fo_overview(self) -> List[Dict]:
        """Get overview of index F&O contracts."""
        results = []
        
        for index_symbol, info in self.index_fo.items():
            try:
                data = self.get_stock_data(info['symbol'], "5d")
                
                if not data.empty and len(data) >= 2:
                    current_price = float(data['Close'].iloc[-1])
                    previous_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
                    price_change = current_price - previous_close
                    price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
                    
                    # Volume with NaN handling
                    try:
                        volume = data['Volume'].iloc[-1]
                        if pd.isna(volume) or volume <= 0:
                            volume = 0
                        else:
                            volume = int(volume)
                    except:
                        volume = 0
                    
                    # Calculate lot value
                    lot_value = current_price * info['lot_size']
                    
                    results.append({
                        'symbol': index_symbol,
                        'name': info['name'],
                        'current_level': round(current_price, 2),
                        'change': round(price_change, 2),
                        'change_pct': round(price_change_percent, 2),
                        'lot_size': info['lot_size'],
                        'lot_value': round(lot_value, 2)
                    })
            except Exception as e:
                print(f"Error fetching {index_symbol}: {e}")
        
        return results
    
    def get_index_fo_data(self) -> List[Dict]:
        """Alias for get_fo_overview for dashboard compatibility."""
        return self.get_fo_overview()
    
    def get_fo_analytics(self, symbol: str) -> Dict:
        """Get comprehensive F&O analytics for a single stock."""
        try:
            result = self.analyze_fo_stock(symbol)
            if result:
                return {
                    'status': 'success',
                    'symbol': symbol,
                    'name': result.get('name', symbol),
                    'sector': result.get('sector', 'Unknown'),
                    'current_price': result.get('current_price', 0),
                    'price_change_pct': result.get('price_change_pct', 0),
                    'volume_ratio': result.get('volume_ratio', 1.0),
                    'historical_volatility': result.get('historical_volatility', 0),
                    'lot_size': result.get('lot_size', 0),
                    'lot_value': result.get('lot_value', 0),
                    'greeks': result.get('greeks', {}),
                    'strikes': result.get('strikes', {}),
                    'signals': result.get('signals', [])
                }
            else:
                return {
                    'status': 'error',
                    'symbol': symbol,
                    'error': 'No data available'
                }
        except Exception as e:
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e)
            }
    
    def get_top_fo_stocks_by_volume(self, min_volume_ratio: float = 1.5, limit: int = 20) -> List[Dict]:
        """Get top F&O stocks by volume activity."""
        results = []
        
        for symbol in list(self.fo_stocks.keys())[:limit]:
            try:
                analytics = self.get_fo_analytics(symbol)
                if analytics['status'] == 'success' and analytics['volume_ratio'] >= min_volume_ratio:
                    results.append(analytics)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by volume ratio descending
        results.sort(key=lambda x: x.get('volume_ratio', 0), reverse=True)
        return results
    
    def get_high_volatility_fo_stocks(self, min_volatility: float = 25.0, limit: int = 20) -> List[Dict]:
        """Get F&O stocks with high volatility."""
        results = []
        
        for symbol in list(self.fo_stocks.keys())[:limit]:
            try:
                analytics = self.get_fo_analytics(symbol)
                if analytics['status'] == 'success' and analytics['historical_volatility'] >= min_volatility:
                    results.append(analytics)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # Sort by volatility descending
        results.sort(key=lambda x: x.get('historical_volatility', 0), reverse=True)
        return results
    
    def get_fo_stocks_by_sector(self, sector: str, limit: int = 10) -> List[str]:
        """Get F&O stock symbols by sector."""
        sector_stocks = []
        for symbol, info in self.fo_stocks.items():
            if info['sector'].lower() == sector.lower():
                sector_stocks.append(symbol)
                if len(sector_stocks) >= limit:
                    break
        return sector_stocks

# Test the module
if __name__ == "__main__":
    analyzer = NiftyFOStocksAnalyzer()
    
    # Test single stock analysis
    result = analyzer.analyze_fo_stock("RELIANCE")
    print("RELIANCE Analysis:", result)
    
    # Test F&O overview
    overview = analyzer.get_fo_overview()
    print("F&O Overview:", overview)
