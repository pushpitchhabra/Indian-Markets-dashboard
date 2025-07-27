"""
Indian Stock Market Dashboard - Main Application
===============================================
A comprehensive Streamlit-based dashboard for Indian stock market analysis and trading.
Features Zerodha API integration, persistent login, and high-volume stock screening.

Author: AI Assistant for Stock Market Analysis
Created: 2025-01-27
"""

import streamlit as st
import os
from datetime import datetime
from kiteconnect import KiteConnect
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import parse_qs
import time
from nifty500_high_volume_stock_screener import MarketDataFetcher, display_market_data_tab
from zerodha_session_manager import (
    initialize_persistent_session, 
    save_current_session, 
    logout_and_clear_session,
    display_session_info
)
from debug_stock_data_fetcher import display_debug_tab
from premarket_dashboard_interface import display_premarket_analysis_interface, display_premarket_quick_view
from premarket_high_volume_analyzer import PreMarketHighVolumeAnalyzer
from premarket_advanced_technical_dashboard import show_advanced_premarket_technical_analysis
from enhanced_premarket_dashboard import show_enhanced_premarket_dashboard
# F&O section removed as requested by user
from performance_monitor import show_performance_monitor
from settings_dashboard import SettingsDashboard

# Page configuration
st.set_page_config(
    page_title="Indian Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .session-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        background: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        z-index: 1000;
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
    """Render the Zerodha API login page with persistent session support"""
    st.markdown('<h1 class="main-header">🚀 Indian Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Check for existing session
    if st.session_state.get('logged_in', False):
        st.success("✅ You are already logged in! Redirecting to dashboard...")
        time.sleep(1)
        st.rerun()
        return
    
    st.markdown("""
    <div class="info-box">
        <h3>📋 Zerodha API Setup Instructions</h3>
        <p><strong>Step 1:</strong> Get your Zerodha API credentials from <a href="https://developers.kite.trade/" target="_blank">Kite Connect Developer Console</a></p>
        <p><strong>Step 2:</strong> Create a new app with redirect URL: <code>http://127.0.0.1:5000/</code></p>
        <p><strong>Step 3:</strong> Enter your API Key and Secret below</p>
        <p><strong>Step 4:</strong> Click the generated login link and complete authentication</p>
        <p><strong>Step 5:</strong> Copy the redirected URL and paste it back here</p>
        <p><strong>✨ Your session will be saved and persist across dashboard refreshes!</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # API credentials input
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input(
            "🔑 API Key", 
            value=st.session_state.api_key,
            placeholder="Enter your Zerodha API Key",
            help="Get this from your Kite Connect app dashboard"
        )
    
    with col2:
        api_secret = st.text_input(
            "🔐 API Secret", 
            value=st.session_state.api_secret,
            type="password",
            placeholder="Enter your Zerodha API Secret",
            help="Keep this secret and secure"
        )
    
    # Store credentials in session state
    st.session_state.api_key = api_key
    st.session_state.api_secret = api_secret
    
    if api_key and api_secret:
        # Generate login URL
        login_url = create_login_url(api_key)
        
        st.markdown("---")
        st.markdown("### 🔗 Step 3: Login to Zerodha")
        
        st.markdown(f"""
        <div class="warning-box">
            <p><strong>Click the link below to login to your Zerodha account:</strong></p>
            <p><a href="{login_url}" target="_blank" style="font-size: 1.2rem; font-weight: bold;">🔗 Login to Zerodha Kite</a></p>
            <p><em>After clicking, you'll be redirected to Zerodha. Login and then copy the full URL from the address bar of the redirected page.</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # URL input for token extraction
        redirect_url = st.text_input(
            "📋 Paste the redirected URL here:",
            placeholder="https://127.0.0.1:5000/?request_token=...",
            help="After logging in to Zerodha, copy the full URL from your browser's address bar and paste it here"
        )
        
        if redirect_url:
            request_token = extract_request_token(redirect_url)
            
            if request_token:
                st.success(f"✅ Request token extracted successfully!")
                
                if st.button("🚀 Complete Login & Save Session", type="primary"):
                    try:
                        # Initialize KiteConnect
                        kite = KiteConnect(api_key=api_key)
                        
                        # Generate access token
                        data = kite.generate_session(request_token, api_secret=api_secret)
                        access_token = data["access_token"]
                        
                        # Set access token
                        kite.set_access_token(access_token)
                        
                        # Get user profile
                        profile = kite.profile()
                        
                        # Store in session state
                        st.session_state.kite = kite
                        st.session_state.access_token = access_token
                        st.session_state.user_profile = profile
                        st.session_state.logged_in = True
                        
                        # Save session for persistence
                        save_current_session()
                        
                        st.success("🎉 Login successful! Session saved. Redirecting to dashboard...")
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
                        st.info("Please check your API credentials and try again.")
            else:
                st.error("❌ Could not extract request token from URL. Please make sure you copied the complete redirected URL.")

def stock_market_dashboard():
    """Render the main stock market dashboard after successful login"""
    
    # Initialize session state variables if not present
    if 'user_id' not in st.session_state:
        if 'user_profile' in st.session_state and st.session_state.user_profile:
            st.session_state.user_id = st.session_state.user_profile.get('user_id', 'Unknown')
        else:
            st.session_state.user_id = 'Demo User'
    
    if 'login_time' not in st.session_state:
        st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Session indicator
    if st.session_state.get('logged_in', False):
        st.markdown('<div class="session-indicator">🟢 Connected</div>', unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">📈 Indian Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # User info sidebar
    with st.sidebar:
        st.markdown("### 📊 Account Information")
        st.write(f"**User ID:** {st.session_state.user_id}")
        st.write(f"**Login Time:** {st.session_state.login_time}")
        st.write(f"**Session Status:** Active ✅")
        
        # Add performance monitor
        show_performance_monitor()
        
        # Display session info
        display_session_info()
        
        # Pre-market quick view
        display_premarket_quick_view(st.session_state.kite)
        
        st.markdown("---")
        st.markdown(f"**🕐 Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("🚪 Logout & Clear Session"):
            logout_and_clear_session()
    
    # Main dashboard content
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Welcome to your Stock Market Dashboard!</h3>
        <p>You are successfully connected to Zerodha Kite API with persistent session.</p>
        <p>✨ Your login will persist even after refreshing the page!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we should show pre-market analysis
    premarket_analyzer = PreMarketHighVolumeAnalyzer(st.session_state.kite)
    market_session = premarket_analyzer.get_market_session()
    
    # Dashboard tabs - F&O section removed as requested
    if market_session == 'closed':
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Overview", "🌅 Pre-Market Analysis", "⚙️ Settings", "🐛 Debug"])
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Overview", "📈 High Volume Stocks", "⚙️ Settings", "🐛 Debug"])
    
    with tab1:
        st.markdown("### 📊 Portfolio Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Portfolio Value", "₹0", "0%")
        
        with col2:
            st.metric("Today's P&L", "₹0", "0%")
        
        with col3:
            st.metric("Available Margin", "₹0", "0%")
        
        with col4:
            st.metric("Used Margin", "₹0", "0%")
        
        st.info("📝 Portfolio data integration will be implemented in the next phase.")
    
    with tab2:
        # Dynamic tab content based on market session
        if market_session == 'closed':
            # Pre-Market Analysis when market is closed
            display_premarket_analysis_interface(st.session_state.kite)
        else:
            # High Volume Stocks during market hours
            display_market_data_tab(st.session_state.kite)
    
    with tab3:
        st.header("⚙️ Settings")
        
        st.subheader("🔐 Session Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Session"):
                if st.session_state.get('session_manager'):
                    restored = st.session_state.session_manager.restore_session_to_streamlit()
                    if restored:
                        st.success("Session refreshed successfully!")
                    else:
                        st.warning("Could not refresh session. Please login again.")
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                logout_and_clear_session()
        
        st.subheader("📊 System Status")
        st.success("✅ Using Zerodha API exclusively")
        st.success("✅ Market status detection working")
        st.success("✅ Pre-market analysis functional")
        st.info("ℹ️ F&O section removed as requested")
        st.info("ℹ️ Technical analysis temporarily disabled")
    
    with tab4:
        st.header("🐛 System Information")
        
        st.subheader("📊 Dashboard Status")
        st.write("**Current Time:**", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        st.write("**Market Session:**", market_session)
        st.write("**API Connection:**", "✅ Connected" if st.session_state.kite else "❌ Not Connected")
        
        if st.session_state.user_profile:
            st.subheader("👤 User Profile")
            st.json(st.session_state.user_profile)
        
        st.subheader("📋 Available Features")
        st.write("✅ Zerodha API Authentication")
        st.write("✅ Pre-market Analysis")
        st.write("✅ Market Status Detection")
        st.write("✅ Session Management")
        st.write("❌ F&O Analytics (Removed)")
        st.write("❌ Technical Analysis (Disabled)")

def main():
    """Main application function with persistent session support"""
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
