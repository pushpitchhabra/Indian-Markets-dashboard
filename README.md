# 📈 Indian Stock Market Dashboard

A comprehensive Streamlit-based dashboard for Indian stock market analysis and trading using Zerodha Kite API. This professional-grade dashboard provides real-time market data, advanced technical analysis, pre-market insights, and F&O analytics.

## 🚀 Features

### ✅ Implemented Features

#### 🔐 Authentication & Security
- Zerodha API Integration with secure login flow
- Persistent session management with encryption
- Automatic session restoration
- Secure credential storage

#### 📊 Market Data & Analysis
- **Real-time Market Data**: Live market indices (Nifty 50, Bank Nifty, etc.)
- **High Volume Stock Screener**: Top 500 stocks with volume filtering
- **Market Session Detection**: Pre-market, live market, and post-market modes
- **Auto-refresh**: Customizable refresh intervals (30s-300s)

#### 🌅 Pre-Market Analysis
- Historical high-volume stock analysis
- Pre-market interest scoring (0-100 scale)
- Last trading day detection with holiday exclusions
- Pre-market preparation tips and recommendations

#### 🔍 Advanced Technical Analysis
- **Multi-timeframe Analysis**: Daily, 30m, 15m, 5m OHLCV data
- **Technical Indicators**: RSI, ADX, MACD, Bollinger Bands, KST, Relative Strength
- **Automated Trading Decisions**: Buy/Sell/Hold with confidence levels
- **Interactive Charts**: Candlestick charts with technical overlays
- **TradingView Integration**: Direct links to charts

#### 💹 Futures & Options (F&O) Analytics
- **F&O Eligible Stocks**: 50+ top F&O stocks with lot sizes
- **Options Greeks**: Delta, Gamma, Theta, Vega calculations
- **Strike Level Analysis**: ITM, ATM, OTM analysis
- **Volatility Analysis**: Historical volatility and ATR
- **Volume Ratio Analysis**: Current vs 20-day average
- **Sector-wise F&O Distribution**: Comprehensive sector mapping

#### 🎯 Stock Universe Management
- **Nifty 500**: Complete 500 stock universe
- **Sectoral Indices**: IT, Banking, Auto, Pharma, FMCG, Metal, Energy
- **Index Weightage Mapping**: Accurate weightage for major indices
- **Flexible Selection**: Up to 500 stocks for analysis

#### 📈 Market Indices Tracker
- Real-time index data with color-coded changes
- Custom gradient backgrounds for performance visualization
- Refresh functionality with timestamps
- Responsive layout for all screen sizes

### 🔮 Future Enhancements
- 🤖 LSTM & Machine Learning Models
- 📋 Advanced Watchlist Management
- 🔔 Real-time Trade Alerts
- 🎯 AI-powered Prediction Models
- ☁️ Cloud Deployment with Multi-user Support

## 📋 Prerequisites

1. **Zerodha Account**: You need an active Zerodha trading account
2. **Kite Connect App**: Create a Kite Connect app at [developers.kite.trade](https://developers.kite.trade/)
3. **Python 3.8+**: Make sure Python is installed on your system

## 🛠️ Installation & Setup

### Step 1: Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd windsurf-project

# Or simply download and extract the project files
```

### Step 2: Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### Step 3: Get Zerodha API Credentials

1. Visit [Kite Connect Developer Console](https://developers.kite.trade/)
2. Login with your Zerodha credentials
3. Create a new app:
   - **App Name**: Your Dashboard Name
   - **App Type**: Connect
   - **Redirect URL**: `http://127.0.0.1:5000/` (important!)
4. Note down your **API Key** and **API Secret**

### Step 4: Run the Dashboard
```bash
# Option 1: Run the main dashboard
streamlit run indian_stock_market_dashboard_main.py

# Option 2: Use the start script (recommended)
python start_dashboard.py

# Option 3: Use the shell script (Mac/Linux)
./run_dashboard.sh
```

## 🔐 How to Login

1. **Start the Dashboard**: Run `streamlit run dashboard.py`
2. **Enter Credentials**: Input your API Key and Secret
3. **Click Login Link**: Click the generated Zerodha login link
4. **Login to Zerodha**: Complete the login process
5. **Copy Redirect URL**: After login, copy the full URL from your browser
6. **Paste URL**: Paste it back in the dashboard
7. **Complete Login**: Click "Complete Login" button

### Example Redirect URL Format:
```
http://127.0.0.1:5000/?request_token=abc123xyz&action=login&status=success
```

## 🎯 Usage Guide

### For Beginners (No Coding Experience)
1. Follow the installation steps exactly as written
2. The dashboard is designed to be self-explanatory
3. All instructions are provided within the app interface
4. If you encounter issues, check the troubleshooting section below

### Dashboard Navigation
- **🏠 Overview Tab**: Account information and portfolio summary
- **📊 Market Data Tab**: Real-time market data with high-volume stock screener
- **🌅 Pre-Market Analysis Tab**: Pre-market insights and historical analysis
- **🔍 Technical Analysis Tab**: Advanced technical indicators and trading signals
- **💹 F&O Analytics Tab**: Futures & Options analysis with Greeks and volatility metrics

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" error**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. "Invalid API credentials" error**
- Double-check your API Key and Secret
- Ensure you're using the correct Kite Connect app credentials
- Verify the redirect URL is set to `http://127.0.0.1:5000/`

**3. "Request token extraction failed"**
- Make sure you copied the complete URL after login
- The URL should contain `request_token=` parameter
- Try the login process again

**4. Dashboard won't start**
```bash
# Check if Streamlit is installed
streamlit --version

# If not installed
pip install streamlit

# Try running with the start script
python start_dashboard.py
```

**5. "No module named 'ta'" or other missing modules**
```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install specific missing modules
pip install ta yfinance plotly
```

## 🏗️ Project Structure

```
windsurf-project/
├── indian_stock_market_dashboard_main.py    # Main Streamlit application
├── zerodha_session_manager.py               # Session management with encryption
├── nifty500_high_volume_stock_screener.py   # Market data and stock screening
├── premarket_high_volume_analyzer.py        # Pre-market analysis engine
├── premarket_technical_analysis_engine.py   # Technical analysis engine
├── fo_dashboard_interface.py                # F&O analytics interface
├── nifty_fo_stocks_analyzer.py             # F&O stocks analysis
├── market_indices_tracker.py               # Real-time indices tracking
├── stock_universe_manager.py               # Stock universe management
├── start_dashboard.py                       # Dashboard launcher script
├── run_dashboard.sh                         # Shell script launcher
├── requirements.txt                         # Python dependencies
├── README.md                               # Project documentation
├── MARKET_DATA_MODULE.md                   # Market data module docs
├── PREMARKET_BUNDLE_README.md              # Pre-market analysis docs
└── .gitignore                              # Git ignore file
```

## 🔮 Future Development Roadmap

### Phase 2: Market Analysis
- Real-time stock data integration
- Technical indicators (RSI, MACD, Bollinger Bands)
- Stock screeners with custom filters

### Phase 3: Machine Learning
- LSTM models for price prediction
- Sentiment analysis integration
- Pattern recognition algorithms

### Phase 4: Trading Features
- Automated trade signals
- Risk management tools
- Portfolio optimization

### Phase 5: Cloud Deployment
- Multi-user support
- Database integration
- Scalable cloud infrastructure

## 🛡️ Security Notes

- Never share your API credentials
- The dashboard stores credentials only in session (not permanently)
- Always logout when done using the dashboard
- Use strong passwords for your Zerodha account

## 📞 Support

This dashboard is designed to be user-friendly for non-programmers. If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are met
3. Verify your Zerodha API setup is correct
4. Make sure your internet connection is stable

## 📄 License

This project is created for educational and personal use. Please comply with Zerodha's API terms of service.

---

**Happy Trading! 📈🚀**
