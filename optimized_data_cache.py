"""
Optimized Data Cache Manager
============================
High-performance caching system for market data with concurrent fetching
and intelligent cache management to speed up dashboard performance.
"""

# Removed yfinance - using only Zerodha API
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

warnings.filterwarnings('ignore')

class OptimizedDataCache:
    """High-performance data cache with concurrent fetching and intelligent caching."""
    
    def __init__(self, cache_duration_minutes: int = 5):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache = {}
        self.cache_timestamps = {}
        self.lock = threading.Lock()
        
        # Pre-defined symbols for faster access
        self.index_symbols = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK", 
            "Sensex": "^BSESN",
            "India VIX": "^INDIAVIX",
            "Nifty IT": "^CNXIT",
            "Nifty Auto": "^CNXAUTO",
            "Nifty Pharma": "^CNXPHARMA",
            "Nifty FMCG": "^CNXFMCG"
        }
        
        # Common F&O stocks for faster access
        self.fo_stocks = [
            "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "HINDUNILVR",
            "ITC", "SBIN", "BHARTIARTL", "ASIANPAINT", "MARUTI", "KOTAKBANK",
            "LT", "AXISBANK", "TITAN", "SUNPHARMA", "ULTRACEMCO", "WIPRO",
            "NTPC", "ONGC", "POWERGRID", "M&M", "TATAMOTORS", "TATASTEEL"
        ]
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache_timestamps:
            return False
        return datetime.now() - self.cache_timestamps[key] < self.cache_duration
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache if valid."""
        with self.lock:
            if self._is_cache_valid(key):
                return self.cache.get(key)
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Set data in cache with timestamp."""
        with self.lock:
            self.cache[key] = data
            self.cache_timestamps[key] = datetime.now()
    
    def fetch_single_stock_data(self, symbol: str, period: str = "5d") -> Dict:
        """Fetch single stock data with caching."""
        cache_key = f"stock_{symbol}_{period}"
        
        # Try cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        try:
            # Try different ticker formats
            for suffix in [".NS", ".BO", ""]:
                try:
                    ticker_symbol = f"{symbol}{suffix}" if suffix else symbol
                    ticker = yf.Ticker(ticker_symbol)
                    data = ticker.history(period=period, interval="1d")
                    
                    if not data.empty and len(data) >= 1:
                        current_price = float(data['Close'].iloc[-1])
                        volume = int(data['Volume'].iloc[-1]) if len(data) >= 1 else 0
                        
                        # Calculate change
                        if len(data) >= 2:
                            previous_close = float(data['Close'].iloc[-2])
                            change = current_price - previous_close
                            change_pct = (change / previous_close) * 100
                        else:
                            change = 0
                            change_pct = 0
                        
                        result = {
                            'symbol': symbol,
                            'price': current_price,
                            'volume': volume,
                            'change': change,
                            'change_pct': change_pct,
                            'data': data,
                            'status': 'success',
                            'timestamp': datetime.now()
                        }
                        
                        # Cache the result
                        self._set_cache(cache_key, result)
                        return result
                        
                except Exception:
                    continue
            
            # If all formats failed
            return {'status': 'error', 'message': f'No data found for {symbol}'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def fetch_multiple_stocks_concurrent(self, symbols: List[str], max_workers: int = 10) -> Dict[str, Dict]:
        """Fetch multiple stocks concurrently for better performance."""
        results = {}
        
        # Check cache first
        uncached_symbols = []
        for symbol in symbols:
            cached = self._get_from_cache(f"stock_{symbol}_5d")
            if cached:
                results[symbol] = cached
            else:
                uncached_symbols.append(symbol)
        
        # Fetch uncached symbols concurrently
        if uncached_symbols:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_symbol = {
                    executor.submit(self.fetch_single_stock_data, symbol): symbol 
                    for symbol in uncached_symbols
                }
                
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result(timeout=10)  # 10 second timeout per stock
                        results[symbol] = result
                    except Exception as e:
                        results[symbol] = {'status': 'error', 'message': str(e)}
        
        return results
    
    def fetch_index_data(self, symbol: str) -> Dict:
        """Fetch index data with caching and error handling."""
        cache_key = f"index_{symbol}"
        
        # Try cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="5d", interval="1d")
            
            if not data.empty and len(data) >= 2:
                current_price = float(data['Close'].iloc[-1])
                previous_close = float(data['Close'].iloc[-2])
                
                change = current_price - previous_close
                change_pct = (change / previous_close) * 100
                
                result = {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_pct,
                    'previous_close': previous_close,
                    'status': 'success',
                    'timestamp': datetime.now()
                }
                
                # Cache the result
                self._set_cache(cache_key, result)
                return result
            
            elif not data.empty:
                # Fallback with single day data
                current_price = float(data['Close'].iloc[-1])
                open_price = float(data['Open'].iloc[-1])
                
                change = current_price - open_price
                change_pct = (change / open_price) * 100 if open_price != 0 else 0
                
                result = {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_pct,
                    'previous_close': open_price,
                    'status': 'success',
                    'timestamp': datetime.now()
                }
                
                self._set_cache(cache_key, result)
                return result
            
            else:
                return {'status': 'error', 'message': 'No data available'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def fetch_all_indices_concurrent(self) -> Dict[str, Dict]:
        """Fetch all indices concurrently for better performance."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_index = {
                executor.submit(self.fetch_index_data, symbol): name 
                for name, symbol in self.index_symbols.items()
            }
            
            for future in as_completed(future_to_index):
                index_name = future_to_index[future]
                try:
                    result = future.result(timeout=5)  # 5 second timeout per index
                    results[index_name] = result
                except Exception as e:
                    results[index_name] = {'status': 'error', 'message': str(e)}
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring."""
        with self.lock:
            total_items = len(self.cache)
            valid_items = sum(1 for key in self.cache.keys() if self._is_cache_valid(key))
            
            return {
                'total_cached_items': total_items,
                'valid_cached_items': valid_items,
                'cache_hit_rate': f"{(valid_items/total_items)*100:.1f}%" if total_items > 0 else "0%",
                'cache_duration_minutes': self.cache_duration.total_seconds() / 60
            }
    
    def clear_cache(self):
        """Clear all cached data."""
        with self.lock:
            self.cache.clear()
            self.cache_timestamps.clear()
    
    def clear_expired_cache(self):
        """Clear only expired cache entries."""
        with self.lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, timestamp in self.cache_timestamps.items()
                if current_time - timestamp >= self.cache_duration
            ]
            
            for key in expired_keys:
                self.cache.pop(key, None)
                self.cache_timestamps.pop(key, None)

# Global cache instance
@st.cache_resource
def get_data_cache():
    """Get or create global data cache instance."""
    return OptimizedDataCache(cache_duration_minutes=3)  # 3-minute cache

# Convenience functions for easy integration
def get_indices_data_fast() -> Dict[str, Dict]:
    """Get all indices data with caching and concurrent fetching."""
    cache = get_data_cache()
    return cache.fetch_all_indices_concurrent()

def get_stocks_data_fast(symbols: List[str]) -> Dict[str, Dict]:
    """Get multiple stocks data with caching and concurrent fetching."""
    cache = get_data_cache()
    return cache.fetch_multiple_stocks_concurrent(symbols)

def get_single_stock_fast(symbol: str) -> Dict:
    """Get single stock data with caching."""
    cache = get_data_cache()
    return cache.fetch_single_stock_data(symbol)

# Test function
if __name__ == "__main__":
    cache = OptimizedDataCache()
    
    print("Testing optimized data cache...")
    
    # Test indices
    print("\n1. Testing indices (concurrent):")
    start_time = time.time()
    indices_data = cache.fetch_all_indices_concurrent()
    end_time = time.time()
    
    print(f"Fetched {len(indices_data)} indices in {end_time - start_time:.2f} seconds")
    for name, data in indices_data.items():
        if data['status'] == 'success':
            print(f"✅ {name}: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
        else:
            print(f"❌ {name}: {data['message']}")
    
    # Test stocks
    print("\n2. Testing stocks (concurrent):")
    test_stocks = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"]
    start_time = time.time()
    stocks_data = cache.fetch_multiple_stocks_concurrent(test_stocks)
    end_time = time.time()
    
    print(f"Fetched {len(stocks_data)} stocks in {end_time - start_time:.2f} seconds")
    for symbol, data in stocks_data.items():
        if data['status'] == 'success':
            print(f"✅ {symbol}: ₹{data['price']:.2f} ({data['change_pct']:+.2f}%)")
        else:
            print(f"❌ {symbol}: {data['message']}")
    
    # Test cache stats
    print(f"\n3. Cache stats: {cache.get_cache_stats()}")
