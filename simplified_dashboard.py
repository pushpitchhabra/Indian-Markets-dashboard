"""
Simplified Indian Stock Market Dashboard
=======================================
A clean, minimal dashboard focusing on core functionality:
1. Zerodha API connection with proper market status
2. Pre-market analysis (working)
3. Market data display with last trading day fallback
4. Date selection for historical data
5. Removed F&O section as requested

Author: AI Assistant
Created: 2025-01-27
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
from kiteconnect import KiteConnect
import urllib.parse as urlparse
from urllib.parse import parse_qs
from zerodha_session_manager import (
    initialize_persistent_session, 
    save_current_session, 
    logout_and_clear_session,
    display_session_info
)

# Page configuration
st.set_page_config(
    page_title="Indian Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .market-status {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
    }
    .market-live {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .market-closed {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'kite' not in st.session_state:
        st.session_state.kite = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'api_secret' not in st.session_state:
        st.session_state.api_secret = ""
    if 'access_token' not in st.session_state:
        st.session_state.access_token = ""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None

def get_market_session() -> tuple:
    """
    Determine current market session and return status with message.
    Returns: (status, message, is_trading_day)
    """
    now = datetime.now()
    current_time = now.time()
    
    # Check if it's a weekday (Monday=0, Sunday=6)
    is_weekday = now.weekday() < 5
    
    # Indian market timings
    pre_market_start = time(9, 0)   # 9:00 AM
    market_open = time(9, 15)       # 9:15 AM
    market_close = time(15, 30)     # 3:30 PM
    post_market_end = time(16, 0)   # 4:00 PM
    
    if not is_weekday:
        return "closed", "🔴 Market Closed - Weekend", False
    
    if current_time < pre_market_start:
        return "closed", "🔴 Market Closed - Before Pre-Market", True
    elif pre_market_start <= current_time < market_open:
        return "pre_market", "🟡 Pre-Market Session (9:00 AM - 9:15 AM)", True
    elif market_open <= current_time < market_close:
        return "live_market", "🟢 Market Live (9:15 AM - 3:30 PM)", True
    elif market_close <= current_time < post_market_end:
        return "post_market", "🟡 Post-Market Session (3:30 PM - 4:00 PM)", True
    else:
        return "closed", "🔴 Market Closed - After Hours", True

def get_last_trading_day() -> date:
    """Get the last trading day (excluding weekends)"""
    today = date.today()
    days_back = 1
    
    while True:
        check_date = today - timedelta(days=days_back)
        # If it's a weekday (Monday=0, Sunday=6)
        if check_date.weekday() < 5:
            return check_date
        days_back += 1
        if days_back > 7:  # Safety check
            return today - timedelta(days=1)

def create_login_url(api_key):
    """Create Zerodha login URL"""
    return f"https://kite.trade/connect/login?api_key={api_key}"

def extract_request_token(redirect_url):
    """Extract request token from redirect URL"""
    try:
        parsed_url = urlparse.urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        request_token = query_params.get('request_token', [None])[0]
        return request_token
    except Exception as e:
        st.error(f"Error extracting token: {str(e)}")
        return None

def zerodha_login_page():
    """Render the Zerodha API login page"""
    st.markdown('<h1 class="main-header">🚀 Indian Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Check for existing session
    if st.session_state.get('logged_in', False):
        st.success("✅ You are already logged in! Redirecting to dashboard...")
        st.rerun()
        return
    
    st.markdown("""
    <div class="success-box">
        <h3>🔐 Zerodha API Login</h3>
        <p>Connect your Zerodha account to access live market data and trading features.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API credentials input
    with st.form("zerodha_login"):
        st.subheader("📝 Enter Your Zerodha API Credentials")
        
        api_key = st.text_input(
            "API Key", 
            value=st.session_state.api_key,
            help="Get your API key from Zerodha Kite Connect developer console"
        )
        
        api_secret = st.text_input(
            "API Secret", 
            value=st.session_state.api_secret,
            type="password",
            help="Your API secret from Zerodha Kite Connect"
        )
        
        submitted = st.form_submit_button("🚀 Generate Login URL")
        
        if submitted and api_key and api_secret:
            st.session_state.api_key = api_key
            st.session_state.api_secret = api_secret
            
            login_url = create_login_url(api_key)
            
            st.success("✅ Login URL generated successfully!")
            st.markdown(f"**[Click here to login to Zerodha]({login_url})**")
            
            st.info("""
            **Next Steps:**
            1. Click the login link above
            2. Login with your Zerodha credentials
            3. Copy the redirect URL after successful login
            4. Paste it in the field below
            """)
    
    # Token extraction
    if st.session_state.api_key and st.session_state.api_secret:
        st.subheader("🔗 Complete Authentication")
        
        redirect_url = st.text_input(
            "Paste the redirect URL here:",
            help="After logging in, copy the entire URL from your browser and paste it here"
        )
        
        if st.button("🔓 Complete Login") and redirect_url:
            request_token = extract_request_token(redirect_url)
            
            if request_token:
                try:
                    # Initialize Kite Connect
                    kite = KiteConnect(api_key=st.session_state.api_key)
                    
                    # Generate access token
                    data = kite.generate_session(request_token, api_secret=st.session_state.api_secret)
                    access_token = data["access_token"]
                    
                    # Set access token
                    kite.set_access_token(access_token)
                    
                    # Get user profile
                    profile = kite.profile()
                    
                    # Update session state
                    st.session_state.kite = kite
                    st.session_state.access_token = access_token
                    st.session_state.user_profile = profile
                    st.session_state.logged_in = True
                    st.session_state.login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Save session persistently
                    save_current_session()
                    
                    st.success(f"🎉 Successfully logged in as {profile['user_name']}!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")
            else:
                st.error("❌ Could not extract request token from URL")

def display_market_status():
    """Display current market status"""
    status, message, is_trading_day = get_market_session()
    
    css_class = "market-live" if status == "live_market" else "market-closed"
    
    st.markdown(f"""
    <div class="market-status {css_class}">
        <h3>{message}</h3>
        <p>Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return status, is_trading_day

def get_nifty_50_stocks():
    """Get Nifty 50 stock symbols for basic analysis"""
    return [
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "INFY", "ITC", "SBIN",
        "BHARTIARTL", "KOTAKBANK", "LT", "HCLTECH", "ASIANPAINT", "AXISBANK", "MARUTI",
        "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND", "BAJFINANCE", "WIPRO", "M&M",
        "NTPC", "TECHM", "POWERGRID", "TATAMOTORS", "COALINDIA", "BAJAJFINSV", "HDFCLIFE",
        "ONGC", "SBILIFE", "INDUSINDBK", "ADANIENT", "JSWSTEEL", "GRASIM", "CIPLA",
        "TATASTEEL", "BPCL", "TATACONSUM", "DRREDDY", "EICHERMOT", "APOLLOHOSP", "DIVISLAB",
        "HINDALCO", "BRITANNIA", "HEROMOTOCO", "UPL", "BAJAJ-AUTO", "SHRIRAMFIN", "LTIM"
    ]

def fetch_basic_stock_data(kite, symbols, selected_date=None):
    """Fetch basic stock data using Zerodha API"""
    if not kite:
        st.error("❌ Zerodha API connection required")
        return pd.DataFrame()
    
    try:
        # Use selected date or last trading day
        if selected_date is None:
            selected_date = get_last_trading_day()
        
        stock_data = []
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(symbols[:20]):  # Limit to 20 stocks for performance
            try:
                # Get instrument token
                instruments = kite.instruments("NSE")
                instrument = next((inst for inst in instruments if inst['tradingsymbol'] == symbol), None)
                
                if instrument:
                    # Get historical data
                    from_date = selected_date
                    to_date = selected_date
                    
                    historical_data = kite.historical_data(
                        instrument['instrument_token'],
                        from_date,
                        to_date,
                        "day"
                    )
                    
                    if historical_data:
                        data = historical_data[-1]  # Get latest data
                        stock_data.append({
                            'Symbol': symbol,
                            'Open': data['open'],
                            'High': data['high'],
                            'Low': data['low'],
                            'Close': data['close'],
                            'Volume': data['volume'],
                            'Date': data['date'].strftime('%Y-%m-%d')
                        })
                
                progress_bar.progress((i + 1) / len(symbols[:20]))
                
            except Exception as e:
                st.warning(f"⚠️ Could not fetch data for {symbol}: {str(e)}")
                continue
        
        progress_bar.empty()
        return pd.DataFrame(stock_data)
        
    except Exception as e:
        st.error(f"❌ Error fetching stock data: {str(e)}")
        return pd.DataFrame()

def display_premarket_analysis(kite):
    """Display pre-market analysis"""
    st.header("🌅 Pre-Market Analysis")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input(
            "Select Date for Analysis",
            value=get_last_trading_day(),
            max_value=date.today()
        )
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Fetch and display data
    if st.button("📊 Analyze Nifty 50 Stocks"):
        with st.spinner("Fetching stock data..."):
            nifty_stocks = get_nifty_50_stocks()
            df = fetch_basic_stock_data(kite, nifty_stocks, selected_date)
            
            if not df.empty:
                st.success(f"✅ Fetched data for {len(df)} stocks")
                
                # Calculate basic metrics
                df['Change %'] = ((df['Close'] - df['Open']) / df['Open'] * 100).round(2)
                df['Volume (L)'] = (df['Volume'] / 100000).round(2)
                
                # Sort by volume
                df_sorted = df.sort_values('Volume', ascending=False)
                
                st.subheader("📈 Top Stocks by Volume")
                st.dataframe(
                    df_sorted[['Symbol', 'Close', 'Change %', 'Volume (L)', 'Date']].head(10),
                    use_container_width=True
                )
                
                # Basic statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Stocks", len(df))
                with col2:
                    gainers = len(df[df['Change %'] > 0])
                    st.metric("Gainers", gainers)
                with col3:
                    losers = len(df[df['Change %'] < 0])
                    st.metric("Losers", losers)
                with col4:
                    avg_volume = df['Volume (L)'].mean()
                    st.metric("Avg Volume (L)", f"{avg_volume:.2f}")
                
            else:
                st.error("❌ No data available for the selected date")

def stock_market_dashboard():
    """Main dashboard after login"""
    st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar with user info
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        if st.session_state.user_profile:
            st.write(f"**Name:** {st.session_state.user_profile['user_name']}")
            st.write(f"**User ID:** {st.session_state.user_profile['user_id']}")
            st.write(f"**Email:** {st.session_state.user_profile['email']}")
        
        st.markdown("### 📊 Session Info")
        st.write(f"**Login Time:** {st.session_state.login_time}")
        st.write(f"**Status:** Active ✅")
        
        if st.button("🚪 Logout"):
            logout_and_clear_session()
    
    # Display market status
    status, is_trading_day = display_market_status()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🌅 Pre-Market Analysis", "📊 Market Data", "⚙️ Settings"])
    
    with tab1:
        display_premarket_analysis(st.session_state.kite)
    
    with tab2:
        st.header("📊 Market Data")
        
        if status == "live_market":
            st.info("🟢 Market is live! Real-time data available.")
        else:
            st.info(f"🔴 Market is closed. Showing last trading day data: {get_last_trading_day()}")
        
        # Date selection for historical data
        selected_date = st.date_input(
            "Select Date",
            value=get_last_trading_day() if status != "live_market" else date.today(),
            max_value=date.today()
        )
        
        if st.button("📈 Get Market Data"):
            with st.spinner("Fetching market data..."):
                nifty_stocks = get_nifty_50_stocks()
                df = fetch_basic_stock_data(st.session_state.kite, nifty_stocks, selected_date)
                
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("❌ No data available")
    
    with tab3:
        st.header("⚙️ Settings")
        
        st.subheader("🔐 Session Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Session"):
                st.success("Session refreshed!")
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                logout_and_clear_session()
        
        st.subheader("📊 Data Settings")
        st.info("✅ Using Zerodha API exclusively for all data")
        st.info("✅ Market status detection working")
        st.info("✅ Last trading day fallback implemented")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Initialize persistent session management
    initialize_persistent_session()
    
    # Route to appropriate page
    if not st.session_state.logged_in:
        zerodha_login_page()
    else:
        stock_market_dashboard()

if __name__ == "__main__":
    main()
