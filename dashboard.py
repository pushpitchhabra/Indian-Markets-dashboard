import streamlit as st
import os
from datetime import datetime
from kiteconnect import KiteConnect
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import parse_qs
import time
from market_data import MarketDataFetcher, display_market_data_tab

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

def login_page():
    """Render the login page"""
    st.markdown('<h1 class="main-header">🚀 Indian Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h3>📋 Setup Instructions</h3>
        <p><strong>Step 1:</strong> Get your Zerodha API credentials from <a href="https://developers.kite.trade/" target="_blank">Kite Connect Developer Console</a></p>
        <p><strong>Step 2:</strong> Enter your API Key and Secret below</p>
        <p><strong>Step 3:</strong> Click the generated login link</p>
        <p><strong>Step 4:</strong> After login, copy the redirected URL and paste it back here</p>
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
                
                if st.button("🚀 Complete Login", type="primary"):
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
                        
                        st.success("🎉 Login successful! Redirecting to dashboard...")
                        time.sleep(2)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
                        st.info("Please check your API credentials and try again.")
            else:
                st.error("❌ Could not extract request token from URL. Please make sure you copied the complete redirected URL.")

def dashboard_page():
    """Render the main dashboard after successful login"""
    st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # User info sidebar
    with st.sidebar:
        st.markdown("### 👤 Account Information")
        if st.session_state.user_profile:
            profile = st.session_state.user_profile
            st.markdown(f"""
            <div class="success-box">
                <p><strong>Name:</strong> {profile.get('user_name', 'N/A')}</p>
                <p><strong>User ID:</strong> {profile.get('user_id', 'N/A')}</p>
                <p><strong>Email:</strong> {profile.get('email', 'N/A')}</p>
                <p><strong>Broker:</strong> {profile.get('broker', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"**🕐 Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("🚪 Logout"):
            # Clear session state
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
    
    # Main dashboard content
    st.markdown("""
    <div class="success-box">
        <h3>🎉 Welcome to your Stock Market Dashboard!</h3>
        <p>You are successfully connected to Zerodha Kite API.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Market Data", "🔍 Analysis", "⚙️ Settings"])
    
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
        
        st.info("📝 Portfolio data will be implemented in the next phase of development.")
    
    with tab2:
        display_market_data_tab(st.session_state.kite)
    
    with tab3:
        st.markdown("### 🔍 Technical Analysis")
        st.info("📊 Technical analysis tools and screeners will be implemented next.")
    
    with tab4:
        st.markdown("### ⚙️ Settings")
        st.info("🛠️ Configuration options will be added here.")

def main():
    """Main application function"""
    initialize_session_state()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
