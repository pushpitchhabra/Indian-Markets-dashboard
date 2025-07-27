# 📈 Market Data Module Documentation

## Overview
The Market Data Module provides comprehensive functionality to fetch, filter, and display high-volume stock data from the Nifty 500 index. It supports pre-market, live market, and post-market sessions with intelligent volume filtering.

## Key Features

### 🎯 **Volume Filtering**
- **Minimum Volume Threshold**: 75,000 shares
- **Automatic Filtering**: Only stocks with volume > 75K are displayed
- **Real-time Updates**: Data refreshes based on market session

### 📊 **Market Sessions Support**
- **Pre-Market**: 9:00 AM - 9:15 AM
- **Live Market**: 9:15 AM - 3:30 PM  
- **Post-Market**: 3:30 PM - 4:00 PM
- **Market Closed**: All other times

### 📈 **Data Sources**
1. **Primary**: Zerodha Kite API (when logged in)
2. **Fallback**: Yahoo Finance API (when Kite unavailable)

## Module Components

### `MarketDataFetcher` Class

#### Core Methods:
- `get_market_session()`: Determines current market session
- `get_high_volume_stocks()`: Fetches filtered stock data
- `get_market_movers()`: Gets top gainers/losers
- `get_volume_leaders()`: Gets highest volume stocks
- `get_market_summary()`: Provides market overview

#### Data Processing:
- Volume formatting (K, L, Cr)
- Price change calculations
- Real-time session detection
- Error handling and fallbacks

### `display_market_data_tab()` Function

#### UI Features:
- **Auto-refresh toggle** with customizable intervals
- **Market status indicator** with color coding
- **Four data views**:
  - Volume Leaders
  - Top Gainers  
  - Top Losers
  - All Stocks
- **Interactive data tables** with formatted columns
- **Real-time updates** and timestamps

## Stock Universe

### Nifty 500 Coverage
- **Top 100 stocks** from Nifty 500 (for demo)
- **Major sectors**: Banking, IT, FMCG, Auto, Pharma, etc.
- **Blue-chip stocks**: RELIANCE, TCS, HDFCBANK, INFY, etc.

### Data Points per Stock:
- Symbol
- Current Price (₹)
- Volume (formatted)
- Price Change (₹ and %)
- High/Low prices
- Market Cap
- Last Updated timestamp

## Usage Examples

### Basic Usage:
```python
from market_data import MarketDataFetcher

# Initialize with Kite connection
fetcher = MarketDataFetcher(kite_instance)

# Get high volume stocks
high_vol_stocks = fetcher.get_high_volume_stocks()

# Get top gainers
gainers = fetcher.get_market_movers("gainers")

# Get market summary
summary = fetcher.get_market_summary()
```

### Streamlit Integration:
```python
from market_data import display_market_data_tab

# Display in Streamlit tab
display_market_data_tab(st.session_state.kite)
```

## Configuration Options

### Volume Threshold:
```python
fetcher = MarketDataFetcher()
fetcher.min_volume = 100000  # Change to 1L minimum
```

### Refresh Intervals:
- 30 seconds (High frequency)
- 60 seconds (Default)
- 120 seconds (Medium)
- 300 seconds (Low frequency)

## Market Session Logic

### Session Detection:
```python
def get_market_session():
    now = datetime.now()
    current_time = now.time()
    
    if 9:00 <= current_time < 9:15:
        return "pre_market"
    elif 9:15 <= current_time < 15:30:
        return "live_market"
    elif 15:30 <= current_time < 16:00:
        return "post_market"
    else:
        return "closed"
```

## Data Accuracy & Reliability

### Primary Source (Kite API):
- ✅ Real-time data
- ✅ Accurate volume figures
- ✅ Pre-market data available
- ✅ Official NSE data

### Fallback Source (Yahoo Finance):
- ✅ Reliable backup
- ⚠️ Slight delay (1-2 minutes)
- ✅ Historical data
- ⚠️ Limited pre-market data

## Performance Optimizations

### Efficient Data Fetching:
- Batch API calls for multiple stocks
- Intelligent caching mechanisms
- Error handling with graceful fallbacks
- Minimal memory footprint

### UI Optimizations:
- Lazy loading for large datasets
- Formatted display columns
- Responsive design
- Auto-refresh controls

## Error Handling

### Common Scenarios:
1. **API Rate Limits**: Automatic retry with backoff
2. **Network Issues**: Fallback to alternative source
3. **Invalid Symbols**: Skip and continue processing
4. **Market Closed**: Display last available data

### User Notifications:
- Clear error messages
- Data source indicators
- Last update timestamps
- Market status warnings

## Future Enhancements

### Planned Features:
- **Historical volume analysis**
- **Volume spike detection**
- **Sector-wise filtering**
- **Custom volume thresholds**
- **Export functionality**
- **Price alerts integration**

### Technical Improvements:
- **WebSocket integration** for real-time updates
- **Database caching** for historical data
- **Advanced filtering options**
- **Performance monitoring**

## Integration with Dashboard

### Current Integration:
- Seamlessly integrated into main dashboard
- Available in "Market Data" tab
- Uses existing Kite connection
- Maintains session state

### User Experience:
- **No additional setup required**
- **Automatic data source selection**
- **Intuitive interface**
- **Real-time updates**

## Troubleshooting

### Common Issues:

**1. No data displayed:**
- Check internet connection
- Verify Kite API login status
- Ensure market is open or recently closed

**2. Slow loading:**
- Reduce refresh frequency
- Check network speed
- Try during off-peak hours

**3. Volume filter too restrictive:**
- Adjust `min_volume` parameter
- Check if market session is active
- Verify stock symbols are correct

### Debug Mode:
```python
# Enable detailed logging
fetcher = MarketDataFetcher(kite, debug=True)
```

## Best Practices

### For Users:
1. **Login to Kite** for best data quality
2. **Use appropriate refresh intervals** (don't overload APIs)
3. **Monitor during active market hours** for best results
4. **Check market session status** before analyzing data

### For Developers:
1. **Handle API errors gracefully**
2. **Implement proper caching**
3. **Use batch requests when possible**
4. **Respect API rate limits**

---

**📊 This module provides a solid foundation for advanced market analysis and trading strategies.**
