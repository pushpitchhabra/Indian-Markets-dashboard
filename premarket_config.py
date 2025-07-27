"""
Pre-Market Configuration Module
===============================
Configuration settings and constants specifically for pre-market analysis modules.
Centralizes all pre-market related settings for easy management and updates.

Author: AI Assistant for Indian Stock Market Pre-Market Analysis
Created: 2025-01-27
"""

from datetime import time, date
from typing import List, Dict

class PreMarketConfig:
    """Configuration class for pre-market analysis settings."""
    
    # Market timing constants
    PREMARKET_START_TIME = time(9, 0)   # 9:00 AM
    MARKET_OPEN_TIME = time(9, 15)      # 9:15 AM
    MARKET_CLOSE_TIME = time(15, 30)    # 3:30 PM
    POSTMARKET_END_TIME = time(16, 0)   # 4:00 PM
    
    # Volume thresholds for pre-market analysis
    MIN_VOLUME_THRESHOLD = 75000        # Minimum 75K volume
    HIGH_VOLUME_THRESHOLD = 1000000     # 10L+ considered high volume
    VERY_HIGH_VOLUME_THRESHOLD = 5000000  # 50L+ considered very high volume
    
    # Price movement thresholds
    BIG_MOVE_THRESHOLD = 3.0           # 3%+ considered significant move
    HIGH_VOLATILITY_THRESHOLD = 5.0    # 5%+ volatility considered high
    
    # Pre-market scoring weights
    VOLUME_WEIGHT = 0.4                # 40% weight for volume
    PRICE_MOVEMENT_WEIGHT = 0.3        # 30% weight for price movement
    VOLATILITY_WEIGHT = 0.3            # 30% weight for volatility
    
    # Indian market holidays 2025 (major ones)
    INDIAN_MARKET_HOLIDAYS_2025 = [
        date(2025, 1, 26),  # Republic Day
        date(2025, 3, 14),  # Holi
        date(2025, 4, 18),  # Good Friday
        date(2025, 8, 15),  # Independence Day
        date(2025, 10, 2),  # Gandhi Jayanti
        date(2025, 11, 1),  # Diwali (approximate)
        date(2025, 12, 25), # Christmas
    ]
    
    # High-liquidity stocks most relevant for pre-market analysis
    PREMARKET_FOCUS_STOCKS = [
        # Banking & Financial Services
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "INDUSINDBK",
        "BAJFINANCE", "BAJAJFINSV", "SBILIFE", "HDFCLIFE",
        
        # Information Technology
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTI", "MINDTREE",
        
        # Oil & Gas
        "RELIANCE", "ONGC", "BPCL", "IOCL", "GAIL",
        
        # Consumer Goods
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO",
        "GODREJCP", "COLPAL", "TATACONSUM",
        
        # Automobiles
        "MARUTI", "TATAMOTORS", "BAJAJ-AUTO", "HEROMOTOCO", "EICHERMOT",
        "MAHINDRA", "ASHOKLEY",
        
        # Pharmaceuticals
        "SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "BIOCON", "LUPIN",
        
        # Metals & Mining
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA", "SAIL", "NMDC",
        
        # Cement
        "ULTRACEMCO", "GRASIM", "ACC", "AMBUJACEMENT",
        
        # Telecom
        "BHARTIARTL", "IDEA",
        
        # Power
        "POWERGRID", "NTPC", "ADANIPOWER",
        
        # Infrastructure
        "LT", "ADANIPORTS",
        
        # Retail & E-commerce
        "DMART", "ZOMATO", "NYKAA", "PAYTM",
        
        # Paints & Chemicals
        "ASIANPAINT", "BERGERPAINTS", "PIDILITIND",
        
        # Airlines
        "INDIGO", "SPICEJET",
        
        # Media & Entertainment
        "ZEEL", "SUNTV", "NETWORK18"
    ]
    
    @classmethod
    def get_volume_category(cls, volume: int) -> str:
        """Categorize volume based on thresholds."""
        if volume >= cls.VERY_HIGH_VOLUME_THRESHOLD:
            return "Very High"
        elif volume >= cls.HIGH_VOLUME_THRESHOLD:
            return "High"
        elif volume >= cls.MIN_VOLUME_THRESHOLD:
            return "Medium"
        else:
            return "Low"
    
    @classmethod
    def is_big_move(cls, price_change_pct: float) -> bool:
        """Check if price movement is considered significant."""
        return abs(price_change_pct) >= cls.BIG_MOVE_THRESHOLD
    
    @classmethod
    def is_high_volatility(cls, volatility_pct: float) -> bool:
        """Check if volatility is considered high."""
        return volatility_pct >= cls.HIGH_VOLATILITY_THRESHOLD
    
    @classmethod
    def calculate_premarket_score(cls, volume: int, price_change_pct: float, volatility_pct: float) -> float:
        """
        Calculate pre-market interest score.
        Returns score from 0-100 based on volume, price movement, and volatility.
        """
        # Volume score (0-40 points)
        if volume >= cls.VERY_HIGH_VOLUME_THRESHOLD:
            volume_score = 40
        elif volume >= cls.HIGH_VOLUME_THRESHOLD:
            volume_score = 30
        elif volume >= cls.MIN_VOLUME_THRESHOLD:
            volume_score = 20
        else:
            volume_score = 10
        
        # Price movement score (0-30 points)
        abs_price_change = abs(price_change_pct)
        if abs_price_change >= 5:
            price_score = 30
        elif abs_price_change >= 3:
            price_score = 25
        elif abs_price_change >= 1:
            price_score = 15
        else:
            price_score = 5
        
        # Volatility score (0-30 points)
        if volatility_pct >= 8:
            volatility_score = 30
        elif volatility_pct >= 5:
            volatility_score = 25
        elif volatility_pct >= 3:
            volatility_score = 15
        else:
            volatility_score = 5
        
        total_score = volume_score + price_score + volatility_score
        return min(100, total_score)  # Cap at 100
    
    @classmethod
    def get_premarket_recommendations(cls, score: float) -> Dict[str, str]:
        """Get recommendations based on pre-market score."""
        if score >= 80:
            return {
                "priority": "Very High",
                "action": "Monitor closely - excellent pre-market candidate",
                "risk": "High reward potential, manage risk carefully",
                "color": "success"
            }
        elif score >= 60:
            return {
                "priority": "High",
                "action": "Good pre-market focus - consider for watchlist",
                "risk": "Moderate risk-reward profile",
                "color": "info"
            }
        elif score >= 40:
            return {
                "priority": "Medium",
                "action": "Secondary consideration - monitor if primary picks unavailable",
                "risk": "Lower priority, moderate activity expected",
                "color": "warning"
            }
        else:
            return {
                "priority": "Low",
                "action": "Low priority for pre-market - consider other options",
                "risk": "Limited activity expected",
                "color": "secondary"
            }

# Pre-market analysis display settings
PREMARKET_DISPLAY_CONFIG = {
    "max_stocks_per_tab": 20,
    "default_analysis_days": 1,
    "max_historical_days": 30,
    "refresh_interval_seconds": 300,  # 5 minutes
    "chart_colors": {
        "positive": "#28a745",
        "negative": "#dc3545",
        "neutral": "#6c757d",
        "volume_high": "#007bff",
        "volume_very_high": "#fd7e14"
    }
}

# Pre-market file organization
PREMARKET_MODULE_INFO = {
    "analyzer": "premarket_high_volume_analyzer.py",
    "interface": "premarket_dashboard_interface.py", 
    "config": "premarket_config.py",
    "description": "Complete pre-market analysis bundle - separate from live market modules"
}
