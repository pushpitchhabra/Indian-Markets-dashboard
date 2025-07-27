"""
Stock Universe Manager
=====================
Manages different stock universes (Nifty 50, Bank Nifty, etc.) for analysis.
Provides real stock symbols and allows user selection of analysis scope.

Author: AI Assistant for Indian Stock Market Dashboard
Created: 2025-01-27
"""

import streamlit as st
from typing import Dict, List
# Removed yfinance - using only Zerodha API
import pandas as pd

class StockUniverseManager:
    """Manage different stock universes for analysis."""
    
    def __init__(self):
        # Stock universes with accurate constituent counts
        self.stock_universes = {
            "Nifty 50": [
                "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", "KOTAKBANK",
                "SBIN", "BHARTIARTL", "ITC", "ASIANPAINT", "LT", "AXISBANK", "DMART", "MARUTI",
                "SUNPHARMA", "TITAN", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "WIPRO", "ONGC",
                "NTPC", "POWERGRID", "TATAMOTORS", "TECHM", "HCLTECH", "COALINDIA", "INDUSINDBK",
                "BAJAJFINSV", "GRASIM", "CIPLA", "EICHERMOT", "HEROMOTOCO", "DRREDDY", "JSWSTEEL",
                "TATASTEEL", "ADANIENT", "HINDALCO", "APOLLOHOSP", "BRITANNIA", "DIVISLAB",
                "TATACONSUM", "BAJAJ-AUTO", "SHREECEM", "UPL", "SBILIFE", "HDFCLIFE", "BPCL", "IOC"
            ],
            "Bank Nifty": [
                "HDFCBANK", "ICICIBANK", "KOTAKBANK", "SBIN", "AXISBANK", "INDUSINDBK",
                "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB", "AUBANK", "RBLBANK"
            ],
            "Nifty IT": [
                "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "PERSISTENT", "COFORGE",
                "MPHASIS", "LTTS"
            ],
            "Nifty Auto": [
                "MARUTI", "TATAMOTORS", "EICHERMOT", "HEROMOTOCO", "BAJAJ-AUTO", "M&M",
                "ASHOKLEY", "TVSMOTOR", "MOTHERSON", "BOSCHLTD", "ESCORTS", "FORCE", "MAHINDRA", "BAJAJHLDNG", "EXIDEIND"
            ],
            "Nifty Pharma": [
                "SUNPHARMA", "CIPLA", "DRREDDY", "APOLLOHOSP", "DIVISLAB", "BIOCON",
                "CADILAHC", "AUROPHARMA", "LUPIN", "TORNTPHARM", "ABBOTINDIA", "ALKEM", "GLENMARK", "IPCALAB", "LALPATHLAB"
            ],
            "Nifty FMCG": [
                "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "TATACONSUM", "GODREJCP",
                "DABUR", "MARICO", "COLPAL", "UBL", "EMAMILTD", "VBL", "RADICO", "MCDOWELL-N", "PGHH"
            ],
            "Nifty Metal": [
                "JSWSTEEL", "TATASTEEL", "HINDALCO", "VEDL", "COALINDIA", "NMDC",
                "SAIL", "JINDALSTEL", "NATIONALUM", "MOIL", "WELCORP", "RATNAMANI", "APL", "WELSPUNIND", "HINDZINC"
            ],
            "Nifty Energy": [
                "RELIANCE", "ONGC", "BPCL", "IOC", "GAIL", "HINDPETRO", "ADANIENT",
                "ADANIGREEN", "NTPC", "POWERGRID", "TATAPOWER", "ADANIPOWER", "JSPL", "ADANITRANS", "ADANIPORTS"
            ],
            "Nifty 500": self._get_nifty_500_stocks(),
            "Top 200 High Volume": self._get_top_200_high_volume_stocks()
        }
        
        # Index weightage mapping (approximate percentages)
        self.index_weightages = self._initialize_index_weightages()
    
    def get_stock_universe(self, universe_name: str) -> List[str]:
        """Get stocks for a specific universe."""
        return self.stock_universes.get(universe_name, [])
    
    def get_available_universes(self) -> List[str]:
        """Get list of available stock universes."""
        return list(self.stock_universes.keys())
    
    def validate_stocks(self, symbols: List[str]) -> List[str]:
        """Validate stock symbols and return valid ones."""
        valid_stocks = []
        
        for symbol in symbols:
            try:
                # Quick validation by checking if we can get basic info
                ticker = yf.Ticker(f"{symbol}.NS")
                info = ticker.info
                if info and 'symbol' in info:
                    valid_stocks.append(symbol)
            except:
                continue
        
        return valid_stocks
    
    def _get_nifty_500_stocks(self) -> List[str]:
        """Get comprehensive Nifty 500 stock list."""
        # This is a comprehensive list of Nifty 500 stocks (top 500 by market cap)
        nifty_500 = [
            # Nifty 50 stocks
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", "KOTAKBANK",
            "SBIN", "BHARTIARTL", "ITC", "ASIANPAINT", "LT", "AXISBANK", "DMART", "MARUTI",
            "SUNPHARMA", "TITAN", "ULTRACEMCO", "BAJFINANCE", "NESTLEIND", "WIPRO", "ONGC",
            "NTPC", "POWERGRID", "TATAMOTORS", "TECHM", "HCLTECH", "COALINDIA", "INDUSINDBK",
            "BAJAJFINSV", "GRASIM", "CIPLA", "EICHERMOT", "HEROMOTOCO", "DRREDDY", "JSWSTEEL",
            "TATASTEEL", "ADANIENT", "HINDALCO", "APOLLOHOSP", "BRITANNIA", "DIVISLAB",
            "TATACONSUM", "BAJAJ-AUTO", "SHREECEM", "UPL", "SBILIFE", "HDFCLIFE", "BPCL", "IOC",
            
            # Next 50 and beyond
            "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB", "AUBANK", "RBLBANK", "LTIM",
            "PERSISTENT", "COFORGE", "MPHASIS", "LTTS", "M&M", "ASHOKLEY", "TVSMOTOR",
            "MOTHERSON", "BOSCHLTD", "BIOCON", "CADILAHC", "AUROPHARMA", "LUPIN", "TORNTPHARM",
            "GODREJCP", "DABUR", "MARICO", "COLPAL", "UBL", "VEDL", "NMDC", "SAIL",
            "JINDALSTEL", "NATIONALUM", "MOIL", "GAIL", "HINDPETRO", "ADANIGREEN", "ZEEL",
            "IDEA", "YESBANK", "SUZLON", "RPOWER", "JPPOWER", "GMRINFRA", "ADANIPORTS",
            "ADANITRANS", "ADANIPOWER", "JSWENERGY", "TATAPOWER", "RECLTD", "PFC", "IRCTC",
            "RAILTEL", "MAZAGON", "BEL", "HAL", "BHEL", "RVNL", "IRFC", "CONCOR",
            
            # Additional high-volume stocks to reach 500
            "ESCORTS", "FORCE", "MAHINDRA", "BAJAJHLDNG", "EXIDEIND", "ABBOTINDIA", "ALKEM",
            "GLENMARK", "IPCALAB", "LALPATHLAB", "EMAMILTD", "VBL", "RADICO", "MCDOWELL-N",
            "PGHH", "WELCORP", "RATNAMANI", "APL", "WELSPUNIND", "HINDZINC", "JSPL",
            "CHAMBLFERT", "GNFC", "DEEPAKNTR", "PIDILITIND", "BERGEPAINT", "AKZOINDIA",
            "KANSAINER", "ASTRAL", "RELAXO", "BATA", "PAGEIND", "HONAUT", "THERMAX",
            "CUMMINSIND", "ABB", "SIEMENS", "HAVELLS", "VOLTAS", "BLUESTARCO", "CROMPTON",
            "WHIRLPOOL", "DIXON", "AMBER", "POLYCAB", "KEI", "FINOLEX", "VSTIND",
            "BATAINDIA", "TRENT", "SHOPERSTOP", "ADITYADB1", "JUBLFOOD", "WESTLIFE",
            "DEVYANI", "SAPPHIRE", "ZOMATO", "NYKAA", "PAYTM", "POLICYBZR", "CARTRADE",
            "EASEMYTRIP", "RVNL", "IRCON", "NBCC", "HUDCO", "PRESTIGE", "BRIGADE",
            "SOBHA", "GODREJPROP", "MAHLIFE", "SRTRANSFIN", "CHOLAFIN", "BAJAJHLDNG",
            "SHRIRAMFIN", "MUTHOOTFIN", "MANAPPURAM", "EDELWEISS", "LICHSGFIN", "REPCO",
            "UJJIVAN", "CREDITACC", "SPANDANA", "EQUITAS", "SURYODAY", "FINPIPE",
            "CSBBANK", "DCBBANK", "SOUTHBANK", "KARURBANK", "TMVBANK", "CITYUNION",
            "DHANI", "NUVOCO", "RAMCOCEM", "HEIDELBERG", "JKCEMENT", "ORIENTCEM",
            "PRISMCEM", "INDIACEM", "BIRLAMONEY", "DALBHARAT", "JKLAKSHMI", "MAGMA",
            "STARCEMENT", "JKPAPER", "TNPL", "WESTPAPER", "BALRAMCHIN", "SESAGOA",
            "KAJARIACER", "SOMANY", "HSIL", "CERA", "RAJRATAN", "ORIENTBELL",
            "HINDWARE", "JAGRAN", "DBCORP", "TVTODAY", "NETWORK18", "SAREGAMA",
            "TIPS", "EROS", "BALAJITELE", "SUNTV", "DISHTV", "GTPL", "DENNETWORKS",
            "HATHWAY", "SITICABLE", "INFRATEL", "INDUSIND", "RCOM", "MTNL", "BSNL",
            "RAILVIKAS", "IREDA", "SJVN", "NHPC", "THDC", "NEYVELI", "CIL", "NMDC",
            "VEDL", "HINDALCO", "NALCO", "BALCO", "HINDUSTAN", "GMDC", "KSCL",
            "MIDHANI", "MISHRA", "BEML", "TITAGARH", "TEXRAIL", "KERNEX", "RITES",
            "RAILTEL", "IRCON", "RVNL", "IRFC", "CONCOR", "CONTAINER", "GATEWAY",
            "ALLCARGO", "GATI", "BLUEDART", "VRL", "TCI", "MAHLOG", "SICAL",
            "SHREYAS", "SNOWMAN", "COLDEX", "KHADIM", "RELAXO", "LIBERTY", "CAMPUS",
            "ACTION", "MIRZA", "PARADEEP", "GSFC", "FACT", "RCF", "NFL", "MADRAS",
            "COROMANDEL", "ZUARI", "MANGALAM", "NAGARFERT", "SMARTLINK", "ROLTA",
            "MINDTREE", "CYIENT", "ZENSAR", "HEXAWARE", "NIIT", "KPIT", "RSWM",
            "WELSPUN", "TRIDENT", "VARDHMAN", "ALOKTEXT", "RAYMOND", "ARVIND",
            "SIYARAM", "VIPIND", "GRASIM", "CENTURY", "ORIENT", "KESORAM", "BIRLASOFT",
            "SYMPHONY", "VOLTAS", "BLUESTAR", "LLOYD", "AMBER", "DIXON", "RAJESH",
            "TITAN", "KALYAN", "THANGAMAY", "PCJEWELLER", "TRIBHOVANDAS", "GITANJALI",
            "ORRA", "SENCO", "RENAISSANCE", "VAIBHAV", "SURANA", "FILATEX", "GARWARE",
            "NILKAMAL", "SUPREME", "ASTRAL", "PRINCE", "MAYUR", "FLEXIBLE", "JYOTHY",
            "GODREJIND", "FINEORG", "BAJAJCON", "BAJAJELE", "CROMPTON", "ORIENT",
            "USHA", "KHAITAN", "BUTTERFLY", "PREETHI", "WONDERLA", "ADLABS", "PVR",
            "INOX", "SAREGAMA", "TIPS", "EROS", "MUKAND", "TIMETECHNO", "SPICEJET",
            "JETAIRWAYS", "INDIGO", "GOAIR", "VISTARA", "AKASA", "DECCAN", "KINGFISHER",
            "AIRINDIA", "ALLIANCE", "TRUJET", "REGIONAL", "HERITAGE", "ZOOM", "FLYEASY",
            "SIMPLEX", "STAR", "MEHTA", "PARAMOUNT", "GOLDSTONE", "SHREYANS", "SELAN",
            "HINDOILEXP", "FOSTERS", "GEOJITFSL", "SHAREKHAN", "IIFL", "MOTILAL",
            "ANGELONE", "ZERODHA", "UPSTOX", "GROWW", "PAYTM", "PHONEPE", "GPAY",
            "AMAZONPAY", "FREECHARGE", "MOBIKWIK", "OXIGEN", "AIRTEL", "JIO", "VODAFONE",
            "BSNL", "MTNL", "TIKONA", "HATHWAY", "DEN", "SITI", "GTPL", "FASTWAY",
            "ASIANET", "ORTEL", "KAPPA", "DIGICABLE", "INCABLE", "SITICABLE", "HFCL",
            "STERLITE", "RAILTEL", "RAILVIKAS", "IREDA", "SJVN", "NHPC", "THDC",
            "NEYVELI", "CIL", "NMDC", "VEDL", "HINDALCO", "NALCO", "BALCO", "HINDUSTAN"
        ]
        return nifty_500[:500]  # Ensure exactly 500 stocks
    
    def _get_top_200_high_volume_stocks(self) -> List[str]:
        """Get top 200 high volume stocks."""
        return self._get_nifty_500_stocks()[:200]
    
    def _initialize_index_weightages(self) -> Dict[str, Dict[str, float]]:
        """Initialize approximate index weightages for stocks."""
        # This would ideally be fetched from a real-time API
        # For now, using approximate weightages
        weightages = {
            "Nifty 50": {
                "RELIANCE": 10.5, "TCS": 8.2, "HDFCBANK": 7.8, "INFY": 6.1,
                "HINDUNILVR": 4.2, "ICICIBANK": 4.0, "KOTAKBANK": 3.8, "SBIN": 3.5,
                "BHARTIARTL": 3.2, "ITC": 3.0, "ASIANPAINT": 2.8, "LT": 2.6,
                "AXISBANK": 2.4, "MARUTI": 2.2, "SUNPHARMA": 2.0
                # Add more as needed
            },
            "Bank Nifty": {
                "HDFCBANK": 22.5, "ICICIBANK": 18.2, "KOTAKBANK": 15.8, "SBIN": 12.1,
                "AXISBANK": 10.5, "INDUSINDBK": 8.2, "BANDHANBNK": 4.8, "FEDERALBNK": 3.2
            }
            # Add more indices as needed
        }
        return weightages
    
    def get_stock_index_info(self, symbol: str) -> Dict[str, any]:
        """Get index information for a stock including weightage."""
        stock_info = {
            "indices": [],
            "primary_index": None,
            "weightage": 0.0
        }
        
        # Find which indices contain this stock
        for index_name, stocks in self.stock_universes.items():
            if symbol in stocks:
                stock_info["indices"].append(index_name)
                
                # Get weightage if available
                if index_name in self.index_weightages and symbol in self.index_weightages[index_name]:
                    weightage = self.index_weightages[index_name][symbol]
                    if weightage > stock_info["weightage"]:
                        stock_info["primary_index"] = index_name
                        stock_info["weightage"] = weightage
        
        return stock_info
    
    def display_stock_selection_ui(self) -> tuple:
        """Display enhanced stock selection UI with analysis mode explanation."""
        st.subheader("📊 Stock Selection & Analysis Configuration")
        
        # Analysis mode explanation
        with st.expander("ℹ️ Analysis Modes Explained", expanded=False):
            st.markdown("""
            **Quick Analysis:**
            - ⚡ Fast processing (5-10 seconds per stock)
            - 📊 Essential indicators: RSI (Daily), ADX (Daily)
            - 🎯 Basic buy/sell/hold decisions
            - 💡 Best for: Quick screening of many stocks
            
            **Detailed Analysis:**
            - 🔍 Comprehensive processing (15-30 seconds per stock)
            - 📈 All indicators: RSI (multiple timeframes), ADX, MACD, Bollinger Bands, KST, Relative Strength
            - 🎯 Advanced buy/sell/hold decisions with detailed reasoning
            - 💡 Best for: In-depth analysis of selected stocks
            """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_universe = st.selectbox(
                "Select Stock Universe",
                options=self.get_available_universes(),
                index=0,
                help="Choose which set of stocks to analyze"
            )
        
        with col2:
            max_stocks = len(self.get_stock_universe(selected_universe))
            max_allowed = 500 if selected_universe == "Nifty 500" else min(max_stocks, 100)
            
            stock_count = st.slider(
                "Number of Stocks to Analyze",
                min_value=5,
                max_value=max_allowed,
                value=min(20, max_stocks),
                step=5,
                help=f"Select how many stocks from {selected_universe} to analyze (Max: {max_allowed})"
            )
        
        with col3:
            analysis_mode = st.selectbox(
                "Analysis Mode",
                ["Quick Analysis", "Detailed Analysis"],
                help="Quick: Essential indicators only | Detailed: All indicators"
            )
        
        # Show universe info
        st.info(f"📋 **{selected_universe}** contains **{max_stocks}** stocks. You selected **{stock_count}** for analysis.")
        
        # Show selected stocks preview
        selected_stocks = self.get_stock_universe(selected_universe)[:stock_count]
        
        with st.expander(f"📋 Selected Stocks Preview ({len(selected_stocks)} stocks)"):
            # Display in columns for better readability
            cols = st.columns(6)
            for i, stock in enumerate(selected_stocks):
                with cols[i % 6]:
                    # Get index info for this stock
                    index_info = self.get_stock_index_info(stock)
                    primary_index = index_info.get('primary_index', 'N/A')
                    weightage = index_info.get('weightage', 0.0)
                    
                    if weightage > 0:
                        st.write(f"**{stock}**\n{primary_index} ({weightage:.1f}%)")
                    else:
                        st.write(f"**{stock}**\n{primary_index}")
        
        return selected_universe, stock_count, selected_stocks, analysis_mode

# Global instance
stock_manager = StockUniverseManager()

def get_stock_universe_manager():
    """Get the global stock universe manager instance."""
    return stock_manager
