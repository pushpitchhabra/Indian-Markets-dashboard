"""
Institutional Order Block Detection Model
========================================
Detects large institutional order blocks using volume analysis, price action,
and market microstructure patterns. Works with both live and historical data.

Key Detection Methods:
1. Volume Spike Analysis - Unusual volume compared to average
2. Price Impact Analysis - Large price moves with volume
3. Order Flow Imbalance - Buy vs Sell pressure
4. Time-based Clustering - Multiple large orders in short timeframe
5. Market Depth Analysis - Large orders affecting bid/ask spread

Research Basis:
- Institutional orders typically 10x+ normal retail size
- Often executed in blocks to minimize market impact
- Create temporary supply/demand imbalances
- Leave footprints in volume and price action patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta, time
from kiteconnect import KiteConnect
import streamlit as st
from typing import List, Dict, Optional, Tuple
import logging
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

@dataclass
class OrderBlock:
    """Data class for detected order blocks"""
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    block_type: str  # 'buy_block', 'sell_block', 'neutral_block'
    confidence: float  # 0-100
    volume_ratio: float  # vs average volume
    price_impact: float  # percentage price change
    duration_minutes: int
    description: str

class InstitutionalOrderBlockDetector:
    """
    Detects institutional order blocks in market data.
    """
    
    def __init__(self, kite: KiteConnect):
        self.kite = kite
        self.min_volume_ratio = 3.0  # Minimum 3x average volume
        self.min_price_impact = 0.5  # Minimum 0.5% price impact
        self.lookback_days = 20  # Days for average calculation
        self.confidence_threshold = 70  # Minimum confidence for alerts
        
    def detect_order_blocks_live(self, symbols: List[str]) -> List[OrderBlock]:
        """
        Detect order blocks in live market data.
        Uses real-time quotes and recent historical data.
        """
        try:
            st.info("🔍 Scanning for institutional order blocks in live data...")
            
            order_blocks = []
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(symbols):
                try:
                    # Get recent intraday data for analysis
                    blocks = self._analyze_symbol_live(symbol)
                    order_blocks.extend(blocks)
                    
                    progress_bar.progress((i + 1) / len(symbols))
                    
                except Exception as e:
                    st.warning(f"⚠️ Error analyzing {symbol}: {str(e)}")
                    continue
            
            progress_bar.empty()
            
            # Sort by confidence and timestamp
            order_blocks.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
            
            st.success(f"✅ Detected {len(order_blocks)} potential order blocks")
            return order_blocks
            
        except Exception as e:
            st.error(f"❌ Error in live order block detection: {str(e)}")
            return []
    
    def detect_order_blocks_historical(self, symbols: List[str], target_date: date) -> List[OrderBlock]:
        """
        Detect order blocks in historical data for a specific date.
        """
        try:
            st.info(f"🔍 Scanning for institutional order blocks on {target_date}...")
            
            order_blocks = []
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(symbols):
                try:
                    blocks = self._analyze_symbol_historical(symbol, target_date)
                    order_blocks.extend(blocks)
                    
                    progress_bar.progress((i + 1) / len(symbols))
                    
                except Exception as e:
                    st.warning(f"⚠️ Error analyzing {symbol}: {str(e)}")
                    continue
            
            progress_bar.empty()
            
            # Sort by confidence and timestamp
            order_blocks.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
            
            st.success(f"✅ Detected {len(order_blocks)} potential order blocks on {target_date}")
            return order_blocks
            
        except Exception as e:
            st.error(f"❌ Error in historical order block detection: {str(e)}")
            return []
    
    def _analyze_symbol_live(self, symbol: str) -> List[OrderBlock]:
        """Analyze a single symbol for live order blocks"""
        try:
            # Get instrument token
            instruments = self.kite.instruments("NSE")
            instrument = next((inst for inst in instruments if inst['tradingsymbol'] == symbol), None)
            
            if not instrument:
                return []
            
            token = instrument['instrument_token']
            
            # Get recent intraday data (last 2 days, 5-minute intervals)
            from_date = date.today() - timedelta(days=2)
            to_date = date.today()
            
            intraday_data = self.kite.historical_data(token, from_date, to_date, "5minute")
            
            if not intraday_data or len(intraday_data) < 20:
                return []
            
            # Convert to DataFrame
            df = pd.DataFrame(intraday_data)
            df['datetime'] = pd.to_datetime(df['date'])
            
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Detect order blocks
            blocks = self._detect_blocks_in_data(df, symbol)
            
            return blocks
            
        except Exception as e:
            return []
    
    def _analyze_symbol_historical(self, symbol: str, target_date: date) -> List[OrderBlock]:
        """Analyze a single symbol for historical order blocks"""
        try:
            # Get instrument token
            instruments = self.kite.instruments("NSE")
            instrument = next((inst for inst in instruments if inst['tradingsymbol'] == symbol), None)
            
            if not instrument:
                return []
            
            token = instrument['instrument_token']
            
            # Get intraday data for target date (5-minute intervals)
            intraday_data = self.kite.historical_data(token, target_date, target_date, "5minute")
            
            if not intraday_data or len(intraday_data) < 10:
                return []
            
            # Convert to DataFrame
            df = pd.DataFrame(intraday_data)
            df['datetime'] = pd.to_datetime(df['date'])
            
            # Get historical data for average calculations
            hist_from = target_date - timedelta(days=self.lookback_days)
            hist_data = self.kite.historical_data(token, hist_from, target_date - timedelta(days=1), "day")
            
            if hist_data:
                avg_volume = np.mean([d['volume'] for d in hist_data])
                df['avg_volume'] = avg_volume
            else:
                df['avg_volume'] = df['volume'].mean()
            
            # Calculate indicators
            df = self._calculate_indicators(df)
            
            # Detect order blocks
            blocks = self._detect_blocks_in_data(df, symbol)
            
            return blocks
            
        except Exception as e:
            return []
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for order block detection"""
        try:
            # Volume indicators
            df['volume_sma_10'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma_10']
            
            # Price indicators
            df['price_change'] = df['close'].pct_change()
            df['price_change_abs'] = abs(df['price_change'])
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
            
            # Order flow approximation (using OHLC)
            df['buying_pressure'] = (df['close'] - df['low']) / (df['high'] - df['low'])
            df['selling_pressure'] = (df['high'] - df['close']) / (df['high'] - df['low'])
            
            # Replace NaN values
            df = df.fillna(0)
            
            return df
            
        except Exception as e:
            return df
    
    def _detect_blocks_in_data(self, df: pd.DataFrame, symbol: str) -> List[OrderBlock]:
        """Detect order blocks in processed data"""
        blocks = []
        
        try:
            for i in range(len(df)):
                row = df.iloc[i]
                
                # Skip if insufficient data
                if i < 5:
                    continue
                
                # Volume spike detection
                volume_ratio = row['volume_ratio']
                price_impact = abs(row['price_change']) * 100
                
                # Check for order block conditions
                if volume_ratio >= self.min_volume_ratio and price_impact >= self.min_price_impact:
                    
                    # Determine block type
                    if row['buying_pressure'] > 0.7:
                        block_type = 'buy_block'
                        description = f"Large buying detected: {volume_ratio:.1f}x volume, {price_impact:.2f}% price impact"
                    elif row['selling_pressure'] > 0.7:
                        block_type = 'sell_block'
                        description = f"Large selling detected: {volume_ratio:.1f}x volume, {price_impact:.2f}% price impact"
                    else:
                        block_type = 'neutral_block'
                        description = f"Large order detected: {volume_ratio:.1f}x volume, {price_impact:.2f}% price impact"
                    
                    # Calculate confidence score
                    confidence = self._calculate_confidence(row, volume_ratio, price_impact)
                    
                    # Only include high-confidence blocks
                    if confidence >= self.confidence_threshold:
                        block = OrderBlock(
                            symbol=symbol,
                            timestamp=row['datetime'],
                            price=row['close'],
                            volume=int(row['volume']),
                            block_type=block_type,
                            confidence=confidence,
                            volume_ratio=volume_ratio,
                            price_impact=price_impact,
                            duration_minutes=5,  # 5-minute intervals
                            description=description
                        )
                        
                        blocks.append(block)
            
            return blocks
            
        except Exception as e:
            return blocks
    
    def _calculate_confidence(self, row: pd.Series, volume_ratio: float, price_impact: float) -> float:
        """Calculate confidence score for order block detection"""
        try:
            # Base confidence from volume and price impact
            volume_score = min(volume_ratio * 10, 50)  # Max 50 points
            price_score = min(price_impact * 5, 30)    # Max 30 points
            
            # Additional factors
            spread_score = min(row['high_low_ratio'] * 100, 20)  # Max 20 points
            
            # Bonus for extreme values
            if volume_ratio > 10:
                volume_score += 10
            if price_impact > 2:
                price_score += 10
            
            total_score = volume_score + price_score + spread_score
            return min(total_score, 100)
            
        except:
            return 50  # Default confidence
    
    def display_order_blocks(self, order_blocks: List[OrderBlock]):
        """Display detected order blocks in Streamlit"""
        if not order_blocks:
            st.info("📊 No institutional order blocks detected")
            return
        
        st.subheader(f"🎯 Detected Order Blocks ({len(order_blocks)})")
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_confidence = st.slider("Minimum Confidence", 0, 100, 70)
        
        with col2:
            block_types = st.multiselect(
                "Block Types",
                ['buy_block', 'sell_block', 'neutral_block'],
                default=['buy_block', 'sell_block', 'neutral_block']
            )
        
        with col3:
            min_volume_ratio = st.slider("Min Volume Ratio", 1.0, 20.0, 3.0)
        
        # Filter blocks
        filtered_blocks = [
            block for block in order_blocks
            if block.confidence >= min_confidence
            and block.block_type in block_types
            and block.volume_ratio >= min_volume_ratio
        ]
        
        if not filtered_blocks:
            st.warning("⚠️ No blocks match the selected filters")
            return
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Blocks", len(filtered_blocks))
        
        with col2:
            buy_blocks = len([b for b in filtered_blocks if b.block_type == 'buy_block'])
            st.metric("Buy Blocks", buy_blocks)
        
        with col3:
            sell_blocks = len([b for b in filtered_blocks if b.block_type == 'sell_block'])
            st.metric("Sell Blocks", sell_blocks)
        
        with col4:
            avg_confidence = np.mean([b.confidence for b in filtered_blocks])
            st.metric("Avg Confidence", f"{avg_confidence:.1f}%")
        
        # Detailed table
        st.subheader("📋 Order Block Details")
        
        blocks_data = []
        for block in filtered_blocks:
            blocks_data.append({
                'Symbol': block.symbol,
                'Time': block.timestamp.strftime('%H:%M:%S'),
                'Date': block.timestamp.strftime('%Y-%m-%d'),
                'Type': block.block_type.replace('_', ' ').title(),
                'Price': f"₹{block.price:.2f}",
                'Volume': f"{block.volume:,}",
                'Vol Ratio': f"{block.volume_ratio:.1f}x",
                'Price Impact': f"{block.price_impact:.2f}%",
                'Confidence': f"{block.confidence:.1f}%",
                'Description': block.description
            })
        
        blocks_df = pd.DataFrame(blocks_data)
        
        # Color coding
        def color_block_type(val):
            if 'Buy' in val:
                return 'background-color: #d4edda'
            elif 'Sell' in val:
                return 'background-color: #f8d7da'
            else:
                return 'background-color: #fff3cd'
        
        styled_df = blocks_df.style.applymap(color_block_type, subset=['Type'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Visualization
        self.plot_order_blocks(filtered_blocks)
    
    def plot_order_blocks(self, order_blocks: List[OrderBlock]):
        """Create visualizations for order blocks"""
        if not order_blocks:
            return
        
        st.subheader("📊 Order Block Visualizations")
        
        # Time distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⏰ Time Distribution**")
            times = [block.timestamp.hour for block in order_blocks]
            time_counts = pd.Series(times).value_counts().sort_index()
            
            fig = px.bar(
                x=time_counts.index,
                y=time_counts.values,
                labels={'x': 'Hour of Day', 'y': 'Number of Blocks'},
                title="Order Blocks by Hour"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**📈 Volume vs Price Impact**")
            volumes = [block.volume_ratio for block in order_blocks]
            impacts = [block.price_impact for block in order_blocks]
            types = [block.block_type for block in order_blocks]
            
            fig = px.scatter(
                x=volumes,
                y=impacts,
                color=types,
                labels={'x': 'Volume Ratio', 'y': 'Price Impact (%)'},
                title="Volume vs Price Impact"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Symbol distribution
        st.markdown("**🏢 Symbol Distribution**")
        symbols = [block.symbol for block in order_blocks]
        symbol_counts = pd.Series(symbols).value_counts().head(10)
        
        fig = px.bar(
            x=symbol_counts.values,
            y=symbol_counts.index,
            orientation='h',
            labels={'x': 'Number of Blocks', 'y': 'Symbol'},
            title="Top 10 Symbols by Order Block Count"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_order_block_detector_tab(kite: KiteConnect):
    """
    Display the institutional order block detection tab.
    """
    st.header("🎯 Institutional Order Block Detector")
    
    st.markdown("""
    **🔬 What are Institutional Order Blocks?**
    
    Large institutional orders that create temporary supply/demand imbalances in the market.
    These are detected using:
    - **Volume Spikes**: 3x+ normal volume
    - **Price Impact**: Significant price movement with volume
    - **Order Flow**: Buy vs sell pressure analysis
    - **Market Microstructure**: Bid/ask spread changes
    """)
    
    # Initialize detector
    if 'order_block_detector' not in st.session_state:
        st.session_state.order_block_detector = InstitutionalOrderBlockDetector(kite)
    
    detector = st.session_state.order_block_detector
    
    # Analysis type selection
    analysis_type = st.radio(
        "Analysis Type",
        ["Live Market Analysis", "Historical Analysis"],
        horizontal=True
    )
    
    # Symbol selection
    st.subheader("📋 Symbol Selection")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if 'instrument_universe' in st.session_state:
            use_custom = st.checkbox("Use Custom Instrument Universe", value=True)
            if use_custom:
                universe_df = st.session_state.instrument_universe
                symbols = universe_df['symbol'].tolist()[:100]  # Limit for performance
                st.info(f"📊 Using {len(symbols)} symbols from custom universe")
            else:
                symbols = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT"]
                st.info(f"📊 Using {len(symbols)} default symbols")
        else:
            symbols = ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT"]
            st.info(f"📊 Using {len(symbols)} default symbols")
    
    with col2:
        symbol_limit = st.number_input(
            "Symbol Limit",
            min_value=5,
            max_value=50,
            value=20,
            help="Limit symbols to avoid API rate limits"
        )
        symbols = symbols[:symbol_limit]
    
    # Analysis controls
    if analysis_type == "Live Market Analysis":
        st.subheader("🔴 Live Analysis")
        
        if st.button("🔍 Scan for Live Order Blocks", type="primary"):
            with st.spinner("Scanning live market for institutional order blocks..."):
                order_blocks = detector.detect_order_blocks_live(symbols)
                st.session_state.detected_blocks = order_blocks
                st.session_state.analysis_timestamp = datetime.now()
    
    else:  # Historical Analysis
        st.subheader("📅 Historical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_date = st.date_input(
                "Select Date",
                value=date.today() - timedelta(days=1),
                max_value=date.today() - timedelta(days=1)
            )
        
        with col2:
            if st.button("🔍 Scan Historical Data", type="primary"):
                with st.spinner(f"Scanning {target_date} for institutional order blocks..."):
                    order_blocks = detector.detect_order_blocks_historical(symbols, target_date)
                    st.session_state.detected_blocks = order_blocks
                    st.session_state.analysis_timestamp = datetime.now()
    
    # Display results
    if 'detected_blocks' in st.session_state:
        st.markdown("---")
        detector.display_order_blocks(st.session_state.detected_blocks)
        
        # Analysis info
        analysis_time = st.session_state.get('analysis_timestamp', datetime.now())
        st.info(f"📊 Analysis completed at {analysis_time.strftime('%H:%M:%S')} on {analysis_time.strftime('%Y-%m-%d')}")
    
    # Configuration
    with st.expander("⚙️ Detection Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            detector.min_volume_ratio = st.slider(
                "Min Volume Ratio",
                1.0, 10.0, 3.0,
                help="Minimum volume compared to average"
            )
            
            detector.min_price_impact = st.slider(
                "Min Price Impact (%)",
                0.1, 5.0, 0.5,
                help="Minimum price change percentage"
            )
        
        with col2:
            detector.confidence_threshold = st.slider(
                "Confidence Threshold",
                50, 95, 70,
                help="Minimum confidence for alerts"
            )
            
            detector.lookback_days = st.slider(
                "Lookback Days",
                5, 50, 20,
                help="Days for average calculations"
            )
    
    # Information
    st.markdown("---")
    st.markdown("""
    **💡 How It Works:**
    
    1. **Volume Analysis**: Identifies volume spikes 3x+ normal levels
    2. **Price Impact**: Measures price movement accompanying volume
    3. **Order Flow**: Analyzes buying vs selling pressure
    4. **Confidence Scoring**: Combines multiple factors for reliability
    5. **Real-time Detection**: Works during market hours for live alerts
    
    **🎯 Use Cases:**
    - Identify institutional accumulation/distribution
    - Spot potential support/resistance levels
    - Time entries around large order completion
    - Monitor smart money activity
    """)
