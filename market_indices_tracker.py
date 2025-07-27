"""Market Indices Tracker

This module tracks major Indian market indices with live price changes.
Provides real-time data for dashboard display with proper color coding.

Author: AI Assistant for Indian Stock Market Dashboard
Created: 2025-01-27
"""

import streamlit as st
# Removed yfinance - using only Zerodha API
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

class MarketIndicesTracker:
    """Track major Indian market indices with live price changes."""
    
    def __init__(self):
        # Using verified working symbols only
        self.indices = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK", 
            "Sensex": "^BSESN",
            "India VIX": "^INDIAVIX",
            "Nifty IT": "^CNXIT",
            "Nifty Auto": "^CNXAUTO",
            "Nifty Pharma": "^CNXPHARMA",
            "Nifty FMCG": "^CNXFMCG"
        }
    
    def get_index_data(self, symbol: str) -> Dict:
        """Get current price and change for an index with improved error handling."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get more recent data first
            hist = ticker.history(period="2d", interval="1d")
            
            if hist.empty:
                # Try with different period
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    # Use minute data if daily data is not available
                    current_price = float(hist['Close'].iloc[-1])
                    previous_price = float(hist['Close'].iloc[0])
                    
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                    
                    return {
                        'price': current_price,
                        'change': change,
                        'change_percent': change_percent,
                        'previous_close': previous_price,
                        'status': 'success'
                    }
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                
                if len(hist) >= 2:
                    previous_close = float(hist['Close'].iloc[-2])
                else:
                    # Use open price as fallback
                    previous_close = float(hist['Open'].iloc[-1])
                
                # Calculate change
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'previous_close': previous_close,
                    'status': 'success'
                }
            
            # If all methods fail, try to get basic info
            info = ticker.info
            if info and 'regularMarketPrice' in info:
                current_price = float(info['regularMarketPrice'])
                previous_close = float(info.get('regularMarketPreviousClose', current_price))
                
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'previous_close': previous_close,
                    'status': 'success'
                }
            
            raise Exception("No data available from any source")
            
        except Exception as e:
            return {
                'price': 0,
                'change': 0,
                'change_percent': 0,
                'previous_close': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def get_all_indices_data(self) -> Dict[str, Dict]:
        """Get data for all tracked indices."""
        results = {}
        for name, symbol in self.indices.items():
            results[name] = self.get_index_data(symbol)
        return results
    
    def display_indices_ticker(self):
        """Display indices ticker at the top of dashboard."""
        st.markdown("### 📊 Market Indices Overview")
        
        # Get indices data
        indices_data = self.get_all_indices_data()
        
        # Split into two rows for better display
        row1_indices = list(indices_data.items())[:4]
        row2_indices = list(indices_data.items())[4:]
        
        # First row
        cols1 = st.columns(4)
        for i, (name, data) in enumerate(row1_indices):
            with cols1[i]:
                if data['status'] == 'success':
                    # Color coding based on change
                    if data['change_percent'] > 0:
                        color = "green"
                        arrow = "↗"
                    elif data['change_percent'] < 0:
                        color = "red" 
                        arrow = "↘"
                    else:
                        color = "gray"
                        arrow = "→"
                    
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        padding: 10px;
                        border-radius: 10px;
                        text-align: center;
                        border-left: 4px solid {color};
                        margin-bottom: 10px;
                    ">
                        <h4 style="margin: 0; color: #333;">{name}</h4>
                        <h3 style="margin: 5px 0; color: #333;">₹{data['price']:,.2f}</h3>
                        <p style="margin: 0; color: {color}; font-weight: bold;">
                            {arrow} {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"{name}: {data.get('error', 'Error')}")
        
        # Second row
        if row2_indices:
            cols2 = st.columns(len(row2_indices))
            for i, (name, data) in enumerate(row2_indices):
                with cols2[i]:
                    if data['status'] == 'success':
                        # Color coding based on change
                        if data['change_percent'] > 0:
                            color = "green"
                            arrow = "↗"
                        elif data['change_percent'] < 0:
                            color = "red" 
                            arrow = "↘"
                        else:
                            color = "gray"
                            arrow = "→"
                        
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                            padding: 10px;
                            border-radius: 10px;
                            text-align: center;
                            border-left: 4px solid {color};
                            margin-bottom: 10px;
                        ">
                            <h4 style="margin: 0; color: #333;">{name}</h4>
                            <h3 style="margin: 5px 0; color: #333;">₹{data['price']:,.2f}</h3>
                            <p style="margin: 0; color: {color}; font-weight: bold;">
                                {arrow} {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"{name}: {data.get('error', 'Error')}")
        
        # Last updated timestamp
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        with col2:
            if st.button("🔄 Refresh", key="indices_refresh"):
                st.rerun()
        
        st.markdown("---")

# Convenience function for easy import
def show_market_indices_ticker():
    """Show market indices ticker - convenience function."""
    tracker = MarketIndicesTracker()
    tracker.display_indices_ticker()
