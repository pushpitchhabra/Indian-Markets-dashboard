"""
Zerodha Session Manager
======================
Handles persistent login sessions for Zerodha Kite API across Streamlit refreshes.
Stores encrypted credentials and access tokens securely.
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
import hashlib
import base64
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
import logging

class ZerodhaSessionManager:
    """
    Manages persistent Zerodha API sessions with secure credential storage.
    Handles automatic token refresh and session validation.
    """
    
    def __init__(self, session_file: str = ".zerodha_session.json"):
        self.session_file = session_file
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Generate or retrieve encryption key for secure storage."""
        key_file = ".session_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def save_session(self, api_key: str, api_secret: str, access_token: str, 
                    user_profile: Dict[str, Any]) -> bool:
        """
        Save encrypted session data to file.
        
        Args:
            api_key: Zerodha API key
            api_secret: Zerodha API secret
            access_token: Generated access token
            user_profile: User profile information
            
        Returns:
            bool: True if saved successfully
        """
        try:
            session_data = {
                'api_key': self._encrypt_data(api_key),
                'api_secret': self._encrypt_data(api_secret),
                'access_token': self._encrypt_data(access_token),
                'user_profile': user_profile,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=1)).isoformat()  # Tokens expire daily
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving session: {str(e)}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt session data from file.
        
        Returns:
            Dict containing session data or None if invalid/expired
        """
        try:
            if not os.path.exists(self.session_file):
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.clear_session()
                return None
            
            # Decrypt sensitive data
            decrypted_data = {
                'api_key': self._decrypt_data(session_data['api_key']),
                'api_secret': self._decrypt_data(session_data['api_secret']),
                'access_token': self._decrypt_data(session_data['access_token']),
                'user_profile': session_data['user_profile'],
                'created_at': session_data['created_at'],
                'expires_at': session_data['expires_at']
            }
            
            return decrypted_data
            
        except Exception as e:
            st.error(f"Error loading session: {str(e)}")
            self.clear_session()
            return None
    
    def validate_session(self, kite: KiteConnect) -> bool:
        """
        Validate if the current session is still active.
        
        Args:
            kite: KiteConnect instance
            
        Returns:
            bool: True if session is valid
        """
        try:
            # Try to fetch user profile to validate session
            profile = kite.profile()
            return profile is not None
            
        except Exception as e:
            logging.warning(f"Session validation failed: {str(e)}")
            return False
    
    def clear_session(self) -> bool:
        """
        Clear stored session data.
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            return True
            
        except Exception as e:
            st.error(f"Error clearing session: {str(e)}")
            return False
    
    def restore_session_to_streamlit(self) -> bool:
        """
        Restore session data to Streamlit session state.
        
        Returns:
            bool: True if session restored successfully
        """
        session_data = self.load_session()
        
        if not session_data:
            return False
        
        try:
            # Initialize KiteConnect with stored credentials
            kite = KiteConnect(api_key=session_data['api_key'])
            kite.set_access_token(session_data['access_token'])
            
            # Validate session is still active
            if not self.validate_session(kite):
                self.clear_session()
                return False
            
            # Restore to Streamlit session state
            st.session_state.kite = kite
            st.session_state.logged_in = True
            st.session_state.api_key = session_data['api_key']
            st.session_state.api_secret = session_data['api_secret']
            st.session_state.access_token = session_data['access_token']
            st.session_state.user_profile = session_data['user_profile']
            
            return True
            
        except Exception as e:
            st.error(f"Error restoring session: {str(e)}")
            self.clear_session()
            return False
    
    def get_session_info(self) -> Optional[Dict[str, str]]:
        """
        Get basic session information for display.
        
        Returns:
            Dict with session info or None
        """
        session_data = self.load_session()
        
        if not session_data:
            return None
        
        return {
            'user_name': session_data['user_profile'].get('user_name', 'Unknown'),
            'user_id': session_data['user_profile'].get('user_id', 'Unknown'),
            'created_at': session_data['created_at'],
            'expires_at': session_data['expires_at']
        }

def initialize_persistent_session():
    """
    Initialize persistent session management for Streamlit app.
    Call this at the start of your Streamlit app.
    """
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = ZerodhaSessionManager()
    
    # Try to restore existing session on app start
    if not st.session_state.get('logged_in', False):
        session_restored = st.session_state.session_manager.restore_session_to_streamlit()
        
        if session_restored:
            st.success("🔄 Previous session restored successfully!")
            st.rerun()

def save_current_session():
    """
    Save current Streamlit session to persistent storage.
    Call this after successful login.
    """
    if ('session_manager' in st.session_state and 
        st.session_state.get('logged_in', False)):
        
        success = st.session_state.session_manager.save_session(
            api_key=st.session_state.api_key,
            api_secret=st.session_state.api_secret,
            access_token=st.session_state.access_token,
            user_profile=st.session_state.user_profile
        )
        
        if success:
            st.success("✅ Session saved - you'll stay logged in on refresh!")

def logout_and_clear_session():
    """
    Logout and clear all session data.
    Call this when user clicks logout.
    """
    if 'session_manager' in st.session_state:
        st.session_state.session_manager.clear_session()
    
    # Clear Streamlit session state
    keys_to_clear = ['kite', 'logged_in', 'api_key', 'api_secret', 
                     'access_token', 'user_profile', 'session_manager']
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("🚪 Logged out successfully!")
    st.rerun()

def display_session_info():
    """
    Display current session information in sidebar.
    """
    if ('session_manager' in st.session_state and 
        st.session_state.get('logged_in', False)):
        
        session_info = st.session_state.session_manager.get_session_info()
        
        if session_info:
            with st.sidebar:
                st.markdown("### 🔐 Session Info")
                st.markdown(f"**User:** {session_info['user_name']}")
                
                created_time = datetime.fromisoformat(session_info['created_at'])
                expires_time = datetime.fromisoformat(session_info['expires_at'])
                
                st.markdown(f"**Login Time:** {created_time.strftime('%H:%M:%S')}")
                st.markdown(f"**Expires:** {expires_time.strftime('%H:%M:%S')}")
                
                # Time remaining
                time_remaining = expires_time - datetime.now()
                hours_remaining = int(time_remaining.total_seconds() // 3600)
                
                if hours_remaining > 0:
                    st.markdown(f"**Time Left:** {hours_remaining}h")
                else:
                    st.warning("⚠️ Session expiring soon!")
