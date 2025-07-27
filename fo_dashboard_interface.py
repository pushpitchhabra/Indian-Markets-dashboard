"""
F&O Dashboard Interface
Comprehensive Futures & Options analysis dashboard for Indian stocks
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from nifty_fo_stocks_analyzer import NiftyFOStocksAnalyzer
from datetime import datetime
import time

class FODashboardInterface:
    """Streamlit interface for F&O analysis dashboard."""
    
    def __init__(self, kite_session=None):
        self.analyzer = NiftyFOStocksAnalyzer(kite_session)
        
    def render_fo_overview(self):
        """Render F&O market overview section."""
        st.header("🎯 F&O Market Overview")
        
        # Index F&O data
        with st.spinner("Loading Index F&O data..."):
            index_data = self.analyzer.get_index_fo_data()
        
        if index_data:
            # Create metrics columns
            cols = st.columns(len(index_data))
            for i, idx in enumerate(index_data):
                with cols[i]:
                    # Color coding
                    color = "green" if idx['change'] >= 0 else "red"
                    delta_color = "normal" if idx['change'] >= 0 else "inverse"
                    
                    st.metric(
                        label=f"**{idx['name']}**",
                        value=f"₹{idx['current_level']:,.2f}",
                        delta=f"{idx['change']:+.2f} ({idx['change_pct']:+.2f}%)",
                        delta_color=delta_color
                    )
                    st.caption(f"Lot Size: {idx['lot_size']} | Lot Value: ₹{idx['lot_value']:,.0f}")
        
        st.markdown("---")
    
    def render_stock_fo_analysis(self):
        """Render individual stock F&O analysis."""
        st.header("📊 Stock F&O Analysis")
        
        # Stock selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_stocks = st.multiselect(
                "Select F&O Stocks for Analysis",
                options=list(self.analyzer.fo_stocks.keys()),
                default=["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"],
                help="Choose up to 10 stocks for detailed F&O analysis"
            )
        
        with col2:
            analysis_type = st.selectbox(
                "Analysis Type",
                ["Quick Overview", "Detailed Analytics", "Options Greeks"]
            )
        
        with col3:
            if st.button("🔄 Refresh Data", type="primary"):
                st.rerun()
        
        if selected_stocks:
            # Limit selection to prevent overload
            if len(selected_stocks) > 10:
                st.warning("⚠️ Please select maximum 10 stocks for optimal performance.")
                selected_stocks = selected_stocks[:10]
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for i, symbol in enumerate(selected_stocks):
                status_text.text(f"Analyzing {symbol}... ({i+1}/{len(selected_stocks)})")
                progress_bar.progress((i + 1) / len(selected_stocks))
                
                analytics = self.analyzer.get_fo_analytics(symbol)
                if analytics['status'] == 'success':
                    results.append(analytics)
                
                time.sleep(0.1)  # Small delay to show progress
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                self.display_fo_results(results, analysis_type)
            else:
                st.error("❌ No data available for selected stocks.")
    
    def display_fo_results(self, results: list, analysis_type: str):
        """Display F&O analysis results."""
        
        if analysis_type == "Quick Overview":
            self.render_quick_overview(results)
        elif analysis_type == "Detailed Analytics":
            self.render_detailed_analytics(results)
        else:  # Options Greeks
            self.render_options_greeks(results)
    
    def render_quick_overview(self, results: list):
        """Render quick overview table."""
        st.subheader("⚡ Quick F&O Overview")
        
        # Create summary DataFrame
        summary_data = []
        for result in results:
            summary_data.append({
                "Symbol": result['symbol'],
                "Name": result['name'][:25] + "..." if len(result['name']) > 25 else result['name'],
                "Sector": result['sector'],
                "Price": f"₹{result['current_price']:,.2f}",
                "Change %": f"{result['price_change_pct']:+.2f}%",
                "Volume Ratio": f"{result['volume_ratio']:.2f}x",
                "Volatility": f"{result['historical_volatility']:.1f}%",
                "Lot Size": result['lot_size'],
                "Lot Value": f"₹{result['lot_value']:,.0f}",
                "Signals": ", ".join(result['signals'][:2]) if result['signals'] else "Normal"
            })
        
        df = pd.DataFrame(summary_data)
        
        # Style the dataframe
        def color_change(val):
            if '+' in str(val):
                return 'color: green'
            elif '-' in str(val):
                return 'color: red'
            return ''
        
        def color_volume(val):
            try:
                vol_val = float(val.replace('x', ''))
                if vol_val > 1.5:
                    return 'color: green; font-weight: bold'
                elif vol_val < 0.8:
                    return 'color: red'
            except:
                pass
            return ''
        
        def color_volatility(val):
            try:
                vol_val = float(val.replace('%', ''))
                if vol_val > 30:
                    return 'color: red; font-weight: bold'
                elif vol_val > 20:
                    return 'color: orange'
            except:
                pass
            return ''
        
        styled_df = df.style.applymap(color_change, subset=['Change %']) \
                           .applymap(color_volume, subset=['Volume Ratio']) \
                           .applymap(color_volatility, subset=['Volatility'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Export option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"fo_quick_overview_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    def render_detailed_analytics(self, results: list):
        """Render detailed analytics with charts."""
        st.subheader("🔍 Detailed F&O Analytics")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        avg_volatility = sum(r['historical_volatility'] for r in results) / len(results)
        high_vol_count = sum(1 for r in results if r['historical_volatility'] > 25)
        high_volume_count = sum(1 for r in results if r['volume_ratio'] > 1.5)
        total_lot_value = sum(r['lot_value'] for r in results)
        
        with col1:
            st.metric("Avg Volatility", f"{avg_volatility:.1f}%")
        with col2:
            st.metric("High Vol Stocks", f"{high_vol_count}/{len(results)}")
        with col3:
            st.metric("High Volume Activity", f"{high_volume_count}/{len(results)}")
        with col4:
            st.metric("Total Lot Value", f"₹{total_lot_value:,.0f}")
        
        # Charts
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Price vs Volatility", "📊 Volume Analysis", "🎯 Strike Levels", "🏭 Sector Distribution"])
        
        with tab1:
            self.render_price_volatility_chart(results)
        
        with tab2:
            self.render_volume_analysis_chart(results)
        
        with tab3:
            self.render_strike_levels_chart(results)
        
        with tab4:
            self.render_sector_distribution_chart(results)
    
    def render_options_greeks(self, results: list):
        """Render options Greeks analysis."""
        st.subheader("🔢 Options Greeks Analysis")
        
        # Greeks summary table
        greeks_data = []
        for result in results:
            greeks = result['greeks']
            greeks_data.append({
                "Symbol": result['symbol'],
                "Name": result['name'][:20] + "..." if len(result['name']) > 20 else result['name'],
                "Current Price": f"₹{result['current_price']:,.2f}",
                "ATM Strike": result['strikes']['ATM'],
                "Delta": f"{greeks['delta']:.3f}",
                "Gamma": f"{greeks['gamma']:.4f}",
                "Theta": f"{greeks['theta']:.2f}",
                "Vega": f"{greeks['vega']:.2f}",
                "Volatility": f"{result['historical_volatility']:.1f}%"
            })
        
        greeks_df = pd.DataFrame(greeks_data)
        st.dataframe(greeks_df, use_container_width=True, hide_index=True)
        
        # Greeks explanation
        with st.expander("📚 Understanding Options Greeks"):
            st.markdown("""
            **Delta (Δ)**: Price sensitivity to underlying stock price changes
            - Range: 0 to 1 for calls, -1 to 0 for puts
            - Higher delta = more sensitive to price changes
            
            **Gamma (Γ)**: Rate of change of delta
            - Higher gamma = delta changes more rapidly
            - Important for risk management
            
            **Theta (Θ)**: Time decay per day
            - Negative for long options (time decay hurts)
            - Shows daily premium erosion
            
            **Vega (ν)**: Sensitivity to volatility changes
            - Higher vega = more sensitive to volatility
            - Important during earnings/events
            """)
    
    def render_price_volatility_chart(self, results: list):
        """Render price vs volatility scatter plot."""
        fig = go.Figure()
        
        for result in results:
            fig.add_trace(go.Scatter(
                x=[result['historical_volatility']],
                y=[result['current_price']],
                mode='markers+text',
                text=[result['symbol']],
                textposition="top center",
                marker=dict(
                    size=result['volume_ratio'] * 10,  # Size based on volume ratio
                    color=result['price_change_pct'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Price Change %")
                ),
                name=result['symbol'],
                hovertemplate=f"<b>{result['symbol']}</b><br>" +
                             f"Price: ₹{result['current_price']:,.2f}<br>" +
                             f"Volatility: {result['historical_volatility']:.1f}%<br>" +
                             f"Volume Ratio: {result['volume_ratio']:.2f}x<br>" +
                             f"Change: {result['price_change_pct']:+.2f}%<extra></extra>"
            ))
        
        fig.update_layout(
            title="Price vs Historical Volatility (Bubble size = Volume Ratio)",
            xaxis_title="Historical Volatility (%)",
            yaxis_title="Current Price (₹)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_volume_analysis_chart(self, results: list):
        """Render volume analysis chart."""
        symbols = [r['symbol'] for r in results]
        volume_ratios = [r['volume_ratio'] for r in results]
        colors = ['green' if vr > 1.5 else 'red' if vr < 0.8 else 'blue' for vr in volume_ratios]
        
        fig = go.Figure(data=[
            go.Bar(
                x=symbols,
                y=volume_ratios,
                marker_color=colors,
                text=[f"{vr:.2f}x" for vr in volume_ratios],
                textposition='auto'
            )
        ])
        
        fig.add_hline(y=1.0, line_dash="dash", line_color="gray", 
                     annotation_text="Average Volume")
        fig.add_hline(y=1.5, line_dash="dash", line_color="green", 
                     annotation_text="High Activity Threshold")
        
        fig.update_layout(
            title="Volume Ratio Analysis (Current vs 20-day Average)",
            xaxis_title="Stock Symbol",
            yaxis_title="Volume Ratio",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_strike_levels_chart(self, results: list):
        """Render strike levels visualization."""
        if not results:
            return
        
        # Select first stock for detailed strike analysis
        selected_stock = st.selectbox(
            "Select stock for strike level analysis:",
            options=[r['symbol'] for r in results],
            key="strike_analysis"
        )
        
        stock_data = next(r for r in results if r['symbol'] == selected_stock)
        strikes = stock_data['strikes']
        current_price = stock_data['current_price']
        
        # Create strike levels chart
        fig = go.Figure()
        
        # Current price line
        fig.add_hline(y=current_price, line_color="blue", line_width=3,
                     annotation_text=f"Current: ₹{current_price:.2f}")
        
        # Strike levels
        strike_colors = {
            'ITM_Call': 'lightgreen',
            'ATM': 'yellow',
            'OTM_Call': 'lightcoral',
            'ITM_Put': 'lightcoral',
            'OTM_Put': 'lightgreen'
        }
        
        for strike_type, strike_price in strikes.items():
            fig.add_hline(
                y=strike_price, 
                line_dash="dash", 
                line_color=strike_colors.get(strike_type, 'gray'),
                annotation_text=f"{strike_type}: ₹{strike_price}"
            )
        
        fig.update_layout(
            title=f"Strike Levels for {selected_stock}",
            yaxis_title="Price (₹)",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_sector_distribution_chart(self, results: list):
        """Render sector distribution pie chart."""
        sector_counts = {}
        for result in results:
            sector = result['sector']
            sector_counts[sector] = sector_counts.get(sector, 0) + 1
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(sector_counts.keys()),
                values=list(sector_counts.values()),
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title="Sector Distribution of Selected F&O Stocks",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_fo_screener(self):
        """Render F&O stock screener."""
        st.header("🔍 F&O Stock Screener")
        
        # Screener options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            screen_type = st.selectbox(
                "Screening Type",
                ["High Volume Activity", "High Volatility", "Sector Analysis"]
            )
        
        with col2:
            if screen_type == "High Volume Activity":
                min_volume_ratio = st.slider("Min Volume Ratio", 1.0, 3.0, 1.5, 0.1)
            elif screen_type == "High Volatility":
                min_volatility = st.slider("Min Volatility (%)", 15.0, 50.0, 25.0, 1.0)
            else:
                selected_sector = st.selectbox(
                    "Select Sector",
                    ["All"] + list(set(info['sector'] for info in self.analyzer.fo_stocks.values()))
                )
        
        with col3:
            max_results = st.slider("Max Results", 5, 25, 15)
        
        if st.button("🔍 Run Screener", type="primary"):
            with st.spinner("Screening F&O stocks..."):
                if screen_type == "High Volume Activity":
                    results = self.analyzer.get_top_fo_stocks_by_volume(limit=max_results)
                    results = [r for r in results if r.get('volume_ratio', 0) >= min_volume_ratio]
                elif screen_type == "High Volatility":
                    results = self.analyzer.get_high_volatility_fo_stocks(
                        min_volatility=min_volatility, limit=max_results
                    )
                else:  # Sector Analysis
                    sector_stocks = self.analyzer.get_fo_sector_analysis()
                    if selected_sector == "All":
                        # Show sector summary
                        st.subheader("📊 Sector-wise F&O Stock Distribution")
                        for sector, stocks in sector_stocks.items():
                            st.write(f"**{sector}**: {len(stocks)} stocks")
                            st.write(", ".join(stocks[:10]) + ("..." if len(stocks) > 10 else ""))
                        return
                    else:
                        # Analyze specific sector
                        sector_symbols = sector_stocks.get(selected_sector, [])[:max_results]
                        results = []
                        for symbol in sector_symbols:
                            analytics = self.analyzer.get_fo_analytics(symbol)
                            if analytics['status'] == 'success':
                                results.append(analytics)
                
                if results:
                    st.success(f"✅ Found {len(results)} stocks matching criteria")
                    self.render_quick_overview(results)
                else:
                    st.warning("⚠️ No stocks found matching the criteria")

def render_fo_dashboard():
    """Main function to render the F&O dashboard."""
    st.set_page_config(
        page_title="F&O Analytics Dashboard",
        page_icon="🎯",
        layout="wide"
    )
    
    st.title("🎯 Futures & Options Analytics Dashboard")
    st.markdown("*Comprehensive analysis of NSE F&O eligible stocks with advanced options analytics*")
    
    dashboard = FODashboardInterface()
    
    # Sidebar for navigation
    st.sidebar.title("📊 F&O Dashboard")
    page = st.sidebar.selectbox(
        "Select Analysis Type",
        ["F&O Overview", "Stock Analysis", "F&O Screener"]
    )
    
    # Add refresh timestamp
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Render selected page
    if page == "F&O Overview":
        dashboard.render_fo_overview()
    elif page == "Stock Analysis":
        dashboard.render_stock_fo_analysis()
    else:  # F&O Screener
        dashboard.render_fo_screener()

if __name__ == "__main__":
    render_fo_dashboard()
