"""
Performance Monitor for Dashboard
================================
Monitor and display performance metrics for the optimized dashboard
"""

import streamlit as st
import time
from datetime import datetime
from optimized_data_cache import get_data_cache, get_indices_data_fast, get_stocks_data_fast

def show_performance_monitor():
    """Display performance monitoring dashboard."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Performance Monitor")
    
    cache = get_data_cache()
    cache_stats = cache.get_cache_stats()
    
    # Cache statistics
    st.sidebar.metric("Cache Hit Rate", cache_stats['cache_hit_rate'])
    st.sidebar.metric("Cached Items", cache_stats['valid_cached_items'])
    
    # Performance test buttons
    if st.sidebar.button("🧪 Test Indices Speed"):
        with st.sidebar:
            with st.spinner("Testing indices..."):
                start_time = time.time()
                indices_data = get_indices_data_fast()
                end_time = time.time()
                
                success_count = sum(1 for data in indices_data.values() if data['status'] == 'success')
                
                st.success(f"✅ {success_count}/8 indices in {end_time - start_time:.2f}s")
    
    if st.sidebar.button("🧪 Test Stocks Speed"):
        with st.sidebar:
            with st.spinner("Testing stocks..."):
                test_stocks = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"]
                start_time = time.time()
                stocks_data = get_stocks_data_fast(test_stocks)
                end_time = time.time()
                
                success_count = sum(1 for data in stocks_data.values() if data['status'] == 'success')
                
                st.success(f"✅ {success_count}/5 stocks in {end_time - start_time:.2f}s")
    
    if st.sidebar.button("🗑️ Clear Cache"):
        cache.clear_cache()
        st.sidebar.success("Cache cleared!")
        st.rerun()

def add_performance_metrics_to_main():
    """Add performance metrics to main dashboard."""
    # This can be called from the main dashboard to show performance info
    cache = get_data_cache()
    cache_stats = cache.get_cache_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⚡ Cache Hit Rate", cache_stats['cache_hit_rate'])
    
    with col2:
        st.metric("📦 Cached Items", f"{cache_stats['valid_cached_items']}/{cache_stats['total_cached_items']}")
    
    with col3:
        st.metric("⏱️ Cache Duration", f"{cache_stats['cache_duration_minutes']:.0f}min")

if __name__ == "__main__":
    st.title("⚡ Performance Monitor")
    
    # Test the optimized system
    st.header("Performance Test Results")
    
    # Test indices
    if st.button("Test Indices Performance"):
        with st.spinner("Testing indices performance..."):
            start_time = time.time()
            indices_data = get_indices_data_fast()
            end_time = time.time()
            
            st.success(f"Fetched {len(indices_data)} indices in {end_time - start_time:.2f} seconds")
            
            # Show results
            for name, data in indices_data.items():
                if data['status'] == 'success':
                    st.write(f"✅ {name}: ₹{data['price']:.2f} ({data['change_percent']:+.2f}%)")
                else:
                    st.write(f"❌ {name}: {data['message']}")
    
    # Test stocks
    if st.button("Test Stocks Performance"):
        with st.spinner("Testing stocks performance..."):
            test_stocks = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"]
            start_time = time.time()
            stocks_data = get_stocks_data_fast(test_stocks)
            end_time = time.time()
            
            st.success(f"Fetched {len(stocks_data)} stocks in {end_time - start_time:.2f} seconds")
            
            # Show results
            for symbol, data in stocks_data.items():
                if data['status'] == 'success':
                    st.write(f"✅ {symbol}: ₹{data['price']:.2f} ({data['change_pct']:+.2f}%)")
                else:
                    st.write(f"❌ {symbol}: {data['message']}")
    
    # Cache stats
    st.header("Cache Statistics")
    cache = get_data_cache()
    cache_stats = cache.get_cache_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Cached Items", cache_stats['total_cached_items'])
        st.metric("Valid Cached Items", cache_stats['valid_cached_items'])
    
    with col2:
        st.metric("Cache Hit Rate", cache_stats['cache_hit_rate'])
        st.metric("Cache Duration", f"{cache_stats['cache_duration_minutes']:.0f} minutes")
