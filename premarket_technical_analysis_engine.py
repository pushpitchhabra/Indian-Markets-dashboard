"""
Pre-Market Technical Analysis Engine
===================================
Advanced technical analysis module for pre-market dashboard featuring:
- OHLCV data analysis
- RSI calculations for multiple timeframes (daily, 30m, 15m, 5m)
- ADX calculations for trend strength
- Automated buy/sell/hold recommendations with explanations
- TradingView integration links

Author: AI Assistant for Indian Stock Market Pre-Market Analysis
Created: 2025-01-27
"""

import pandas as pd
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
import ta
from ta.utils import dropna
from optimized_data_cache import get_single_stock_fast, get_stocks_data_fast
try:
    from kiteconnect import KiteConnect
except ImportError:
    KiteConnect = None
warnings.filterwarnings('ignore')

class PreMarketTechnicalAnalysisEngine:
    """
    Advanced technical analysis engine for pre-market stock analysis.
    Provides comprehensive technical indicators and trading recommendations.
    """
    
    def __init__(self, kite = None):
        self.kite = kite
        
    def get_ohlcv_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get OHLCV data for a stock using optimized caching."""
        try:
            # Use optimized cache for faster data retrieval
            result = get_single_stock_fast(symbol)
            if result['status'] == 'success' and 'data' in result:
                data = result['data']
                if not data.empty and len(data) > 20:  # Need sufficient data
                    print(f"✅ Successfully fetched {len(data)} data points for {symbol} (cached)")
                    # Clean and validate data
                    data = data.dropna()
                    return data
                else:
                    print(f"⚠️ Insufficient cached data for {symbol}: {len(data) if not data.empty else 0} points")
            
            # Fallback to direct fetch if cache fails
            ticker_formats = [f"{symbol}.NS", f"{symbol}.BO", symbol]
            
            for ticker_symbol in ticker_formats:
                try:
                    print(f"Fallback: Trying to fetch data for {ticker_symbol}...")
                    ticker = yf.Ticker(ticker_symbol)
                    data = ticker.history(period=period, interval=interval)
                    
                    if not data.empty and len(data) > 20:  # Need sufficient data
                        print(f"✅ Successfully fetched {len(data)} data points for {ticker_symbol}")
                        # Clean and validate data
                        data = data.dropna()
                        return data
                    else:
                        print(f"⚠️ Insufficient data for {ticker_symbol}: {len(data) if not data.empty else 0} points")
                        
                except Exception as e:
                    print(f"❌ Error with {ticker_symbol}: {str(e)}")
                    continue
            
            print(f"❌ All methods failed for {symbol}")
            return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Critical error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)."""
        try:
            if data.empty or len(data) < period:
                return np.nan
            
            rsi = ta.momentum.RSIIndicator(close=data['Close'], window=period)
            return round(rsi.rsi().iloc[-1], 2)
        except:
            return np.nan
    
    def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate ADX (Average Directional Index)."""
        try:
            if data.empty or len(data) < period:
                return np.nan
            
            adx = ta.trend.ADXIndicator(
                high=data['High'], 
                low=data['Low'], 
                close=data['Close'], 
                window=period
            )
            return round(adx.adx().iloc[-1], 2)
        except:
            return np.nan
    
    def calculate_macd(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate MACD indicators."""
        try:
            if data.empty or len(data) < 26:
                return {'macd': np.nan, 'signal': np.nan, 'histogram': np.nan}
            
            macd = ta.trend.MACD(close=data['Close'])
            return {
                'macd': round(macd.macd().iloc[-1], 4),
                'signal': round(macd.macd_signal().iloc[-1], 4),
                'histogram': round(macd.macd_diff().iloc[-1], 4)
            }
        except:
            return {'macd': np.nan, 'signal': np.nan, 'histogram': np.nan}
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        try:
            if data.empty or len(data) < period:
                return {'upper': np.nan, 'middle': np.nan, 'lower': np.nan, 'position': np.nan}
            
            bb = ta.volatility.BollingerBands(close=data['Close'], window=period)
            current_price = data['Close'].iloc[-1]
            upper = bb.bollinger_hband().iloc[-1]
            lower = bb.bollinger_lband().iloc[-1]
            middle = bb.bollinger_mavg().iloc[-1]
            
            # Calculate position within bands (0-100%)
            position = ((current_price - lower) / (upper - lower)) * 100 if upper != lower else 50
            
            return {
                'upper': round(upper, 2),
                'middle': round(middle, 2),
                'lower': round(lower, 2),
                'position': round(position, 1)
            }
        except:
            return {'upper': np.nan, 'middle': np.nan, 'lower': np.nan, 'position': np.nan}
    
    def calculate_support_resistance(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate basic support and resistance levels."""
        try:
            if data.empty or len(data) < 20:
                return {'support': np.nan, 'resistance': np.nan}
            
            # Simple support/resistance based on recent highs and lows
            recent_data = data.tail(20)
            support = recent_data['Low'].min()
            resistance = recent_data['High'].max()
            
            return {
                'support': round(support, 2),
                'resistance': round(resistance, 2)
            }
        except:
            return {'support': np.nan, 'resistance': np.nan}
    
    def calculate_kst(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate KST (Know Sure Thing) indicator."""
        try:
            if data.empty or len(data) < 100:  # Need enough data for KST
                return {'kst': np.nan, 'kst_signal': np.nan, 'kst_histogram': np.nan}
            
            # KST calculation using different ROC periods
            close = data['Close']
            
            # ROC calculations for different periods
            roc1 = close.pct_change(10) * 100  # 10-period ROC
            roc2 = close.pct_change(15) * 100  # 15-period ROC
            roc3 = close.pct_change(20) * 100  # 20-period ROC
            roc4 = close.pct_change(30) * 100  # 30-period ROC
            
            # Moving averages of ROCs
            ma1 = roc1.rolling(10).mean()
            ma2 = roc2.rolling(10).mean()
            ma3 = roc3.rolling(10).mean()
            ma4 = roc4.rolling(15).mean()
            
            # KST calculation with weights
            kst = (ma1 * 1) + (ma2 * 2) + (ma3 * 3) + (ma4 * 4)
            kst_signal = kst.rolling(9).mean()  # 9-period signal line
            kst_histogram = kst - kst_signal
            
            return {
                'kst': round(kst.iloc[-1], 2) if not pd.isna(kst.iloc[-1]) else np.nan,
                'kst_signal': round(kst_signal.iloc[-1], 2) if not pd.isna(kst_signal.iloc[-1]) else np.nan,
                'kst_histogram': round(kst_histogram.iloc[-1], 2) if not pd.isna(kst_histogram.iloc[-1]) else np.nan
            }
        except Exception as e:
            return {'kst': np.nan, 'kst_signal': np.nan, 'kst_histogram': np.nan}
    
    def calculate_relative_strength(self, symbol: str, benchmark: str = "^NSEI", period: int = 55) -> Dict[str, float]:
        """Calculate relative strength vs benchmark (default Nifty)."""
        try:
            # Fetch stock data
            stock_data = self.get_ohlcv_data(symbol, period=f"{period*2}d", interval="1d")
            
            # Fetch benchmark data (Nifty)
            if benchmark == "^NSEI":
                benchmark_ticker = "^NSEI"
            elif benchmark == "^NSEBANK":
                benchmark_ticker = "^NSEBANK"
            elif benchmark == "^CNXIT":
                benchmark_ticker = "^CNXIT"
            else:
                benchmark_ticker = benchmark
            
            benchmark_data = yf.Ticker(benchmark_ticker).history(period=f"{period*2}d", interval="1d")
            
            if stock_data.empty or benchmark_data.empty:
                return {'relative_strength': np.nan, 'rs_rank': np.nan, 'outperformance': np.nan}
            
            # Align data by date
            common_dates = stock_data.index.intersection(benchmark_data.index)
            if len(common_dates) < period:
                return {'relative_strength': np.nan, 'rs_rank': np.nan, 'outperformance': np.nan}
            
            stock_aligned = stock_data.loc[common_dates]['Close']
            benchmark_aligned = benchmark_data.loc[common_dates]['Close']
            
            # Calculate relative strength over the specified period
            if len(stock_aligned) >= period:
                stock_return = (stock_aligned.iloc[-1] / stock_aligned.iloc[-period] - 1) * 100
                benchmark_return = (benchmark_aligned.iloc[-1] / benchmark_aligned.iloc[-period] - 1) * 100
                
                relative_strength = stock_return - benchmark_return
                
                # Calculate RS rank (0-100 scale)
                rs_rank = 50 + (relative_strength / 2)  # Simplified ranking
                rs_rank = max(0, min(100, rs_rank))  # Clamp between 0-100
                
                # Determine outperformance
                outperformance = "Outperforming" if relative_strength > 0 else "Underperforming"
                
                return {
                    'relative_strength': round(relative_strength, 2),
                    'rs_rank': round(rs_rank, 1),
                    'outperformance': outperformance,
                    'stock_return': round(stock_return, 2),
                    'benchmark_return': round(benchmark_return, 2)
                }
            
            return {'relative_strength': np.nan, 'rs_rank': np.nan, 'outperformance': np.nan}
            
        except Exception as e:
            return {'relative_strength': np.nan, 'rs_rank': np.nan, 'outperformance': np.nan}
    
    def get_comprehensive_analysis(self, symbol: str, benchmark: str = "^NSEI", rs_period: int = 55) -> Dict:
        """
        Get comprehensive technical analysis for a stock across multiple timeframes.
        """
        try:
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'timeframes': {}
            }

            # Define timeframes to analyze - start with daily which is most important
            timeframes = {
                'daily': {'period': '1y', 'interval': '1d'},  # More data for better calculations
                '30m': {'period': '60d', 'interval': '30m'},
                '15m': {'period': '30d', 'interval': '15m'},
                '5m': {'period': '10d', 'interval': '5m'}
            }

            # Process daily timeframe first as it's most critical
            for tf_name in ['daily', '30m', '15m', '5m']:
                if tf_name not in timeframes:
                    continue

                tf_config = timeframes[tf_name]
                try:
                    # Get OHLCV data for this timeframe
                    data = self.get_ohlcv_data(symbol, tf_config['period'], tf_config['interval'])

                    if data.empty or len(data) < 10:
                        print(f"Insufficient data for {symbol} {tf_name}: {len(data) if not data.empty else 0} points")
                        continue

                    print(f"Processing {symbol} {tf_name}: {len(data)} data points")

                    # Calculate indicators for this timeframe
                    indicators = {}

                    # RSI for all timeframes
                    rsi_val = self.calculate_rsi(data)
                    if not np.isnan(rsi_val):
                        indicators['rsi'] = rsi_val

                    # ADX for daily and 30m only
                    if tf_name in ['daily', '30m']:
                        adx_val = self.calculate_adx(data)
                        if not np.isnan(adx_val):
                            indicators['adx'] = adx_val

                    # Additional indicators for daily timeframe
                    if tf_name == 'daily':
                        # MACD
                        macd_data = self.calculate_macd(data)
                        if not all(np.isnan(list(macd_data.values()))):
                            indicators['macd'] = macd_data

                        # Bollinger Bands
                        bb_data = self.calculate_bollinger_bands(data)
                        if not all(np.isnan([v for v in bb_data.values() if isinstance(v, (int, float))])):
                            indicators['bollinger_bands'] = bb_data

                        # Support/Resistance
                        sr_data = self.calculate_support_resistance(data)
                        if not all(np.isnan(list(sr_data.values()))):
                            indicators['support_resistance'] = sr_data

                        # KST
                        kst_data = self.calculate_kst(data)
                        if not all(np.isnan(list(kst_data.values()))):
                            indicators['kst'] = kst_data

                        # Calculate relative strength
                        rs_data = self.calculate_relative_strength(symbol, benchmark, rs_period)
                        if rs_data and not all(np.isnan([v for v in rs_data.values() if isinstance(v, (int, float))])):
                            indicators['relative_strength'] = rs_data

                    # OHLCV summary
                    latest = data.iloc[-1]
                    ohlcv = {
                        'open': round(float(latest['Open']), 2),
                        'high': round(float(latest['High']), 2),
                        'low': round(float(latest['Low']), 2),
                        'close': round(float(latest['Close']), 2),
                        'volume': int(latest['Volume']),
                        'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name)
                    }

                    analysis['timeframes'][tf_name] = {
                        'indicators': indicators,
                        'ohlcv': ohlcv,
                        'data_points': len(data)
                    }

                    print(f"Successfully processed {symbol} {tf_name} with {len(indicators)} indicators")

                except Exception as e:
                    print(f"Error processing {symbol} {tf_name}: {str(e)}")
                    continue

            return analysis

        except Exception as e:
            print(f"Error in comprehensive analysis for {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'timeframes': {},
                'error': str(e)
            }
    
    def generate_trading_decision(self, analysis: Dict) -> Dict[str, str]:
        """
        Generate automated buy/sell/hold decision with detailed explanation.
        """
        try:
            daily_data = analysis['timeframes'].get('daily', {})
            min30_data = analysis['timeframes'].get('30m', {})

            if 'error' in daily_data or 'indicators' not in daily_data:
                min30_data = analysis['timeframes'].get('30min', {})
                
                if 'error' in daily_data or 'indicators' not in daily_data:
                    return {
                        'decision': 'HOLD',
                        'confidence': 'Low',
                        'reason': 'Insufficient data for analysis',
                        'score': 0
                    }
            
            daily_indicators = daily_data['indicators']
            min30_indicators = min30_data.get('indicators', {}) if '30min' in analysis['timeframes'] else {}
            
            # Scoring system
            bullish_signals = 0
            bearish_signals = 0
            reasons = []
            
            # RSI Analysis
            daily_rsi = daily_indicators.get('rsi', np.nan)
            if not np.isnan(daily_rsi):
                if daily_rsi < 30:
                    bullish_signals += 2
                    reasons.append(f"Daily RSI oversold ({daily_rsi:.1f})")
                elif daily_rsi > 70:
                    bearish_signals += 2
                    reasons.append(f"Daily RSI overbought ({daily_rsi:.1f})")
                elif 40 <= daily_rsi <= 60:
                    bullish_signals += 1
                    reasons.append(f"Daily RSI neutral-bullish ({daily_rsi:.1f})")
            
            # ADX Analysis (Trend Strength)
            daily_adx = daily_indicators.get('adx', np.nan)
            if not np.isnan(daily_adx):
                if daily_adx > 25:
                    reasons.append(f"Strong trend (ADX: {daily_adx:.1f})")
                    if daily_rsi > 50:
                        bullish_signals += 1
                    else:
                        bearish_signals += 1
                else:
                    reasons.append(f"Weak trend (ADX: {daily_adx:.1f})")
            
            # MACD Analysis
            macd_data = daily_indicators.get('macd', {})
            if macd_data.get('macd') is not None and macd_data.get('signal') is not None:
                macd_val = macd_data['macd']
                signal_val = macd_data['signal']
                
                if macd_val > signal_val:
                    bullish_signals += 1
                    reasons.append("MACD bullish crossover")
                else:
                    bearish_signals += 1
                    reasons.append("MACD bearish crossover")
            
            # Bollinger Bands Analysis
            bb_data = daily_indicators.get('bollinger_bands', {})
            bb_position = bb_data.get('position', np.nan)
            if not np.isnan(bb_position):
                if bb_position < 20:
                    bullish_signals += 1
                    reasons.append(f"Near lower Bollinger Band ({bb_position:.1f}%)")
                elif bb_position > 80:
                    bearish_signals += 1
                    reasons.append(f"Near upper Bollinger Band ({bb_position:.1f}%)")
            
            # Support/Resistance Analysis
            sr_data = daily_indicators.get('support_resistance', {})
            current_price = daily_data['ohlcv']['close']
            support = sr_data.get('support', np.nan)
            resistance = sr_data.get('resistance', np.nan)
            
            if not np.isnan(support) and not np.isnan(resistance):
                price_position = (current_price - support) / (resistance - support) * 100
                if price_position < 25:
                    bullish_signals += 1
                    reasons.append(f"Near support level (₹{support:.2f})")
                elif price_position > 75:
                    bearish_signals += 1
                    reasons.append(f"Near resistance level (₹{resistance:.2f})")
            
            # 30-min timeframe confirmation
            if min30_indicators:
                min30_rsi = min30_indicators.get('rsi', np.nan)
                if not np.isnan(min30_rsi):
                    if daily_rsi < 40 and min30_rsi < 40:
                        bullish_signals += 1
                        reasons.append("Multi-timeframe oversold confirmation")
                    elif daily_rsi > 60 and min30_rsi > 60:
                        bearish_signals += 1
                        reasons.append("Multi-timeframe overbought confirmation")
            
            # Calculate final decision
            net_score = bullish_signals - bearish_signals
            total_signals = bullish_signals + bearish_signals
            
            if net_score >= 2:
                decision = "BUY"
                confidence = "High" if net_score >= 3 else "Medium"
            elif net_score <= -2:
                decision = "SELL"
                confidence = "High" if net_score <= -3 else "Medium"
            else:
                decision = "HOLD"
                confidence = "Medium" if total_signals >= 3 else "Low"
            
            return {
                'decision': decision,
                'confidence': confidence,
                'reason': '; '.join(reasons) if reasons else 'Neutral technical indicators',
                'score': net_score,
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals
            }
            
        except Exception as e:
            return {
                'decision': 'HOLD',
                'confidence': 'Low',
                'reason': f'Analysis error: {str(e)}',
                'score': 0
            }
    
    def get_tradingview_link(self, symbol: str) -> str:
        """Generate TradingView link for the stock."""
        return f"https://www.tradingview.com/chart/?symbol=NSE%3A{symbol}"
    
    def format_technical_summary(self, analysis: Dict) -> Dict[str, str]:
        """Format technical analysis into a readable summary."""
        try:
            daily = analysis['timeframes'].get('daily', {})
            if 'indicators' not in daily:
                return {'summary': 'No data available'}
            
            indicators = daily['indicators']
            ohlcv = daily['ohlcv']
            
            # Create summary
            summary_parts = []
            
            # Price info
            summary_parts.append(f"Price: ₹{ohlcv['close']} (H: ₹{ohlcv['high']}, L: ₹{ohlcv['low']})")
            
            # RSI
            rsi = indicators.get('rsi', np.nan)
            if not np.isnan(rsi):
                rsi_status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                summary_parts.append(f"RSI: {rsi:.1f} ({rsi_status})")
            
            # ADX
            adx = indicators.get('adx', np.nan)
            if not np.isnan(adx):
                trend_strength = "Strong" if adx > 25 else "Weak"
                summary_parts.append(f"ADX: {adx:.1f} ({trend_strength} trend)")
            
            # Bollinger Bands
            bb = indicators.get('bollinger_bands', {})
            bb_pos = bb.get('position', np.nan)
            if not np.isnan(bb_pos):
                bb_status = "Lower band" if bb_pos < 20 else "Upper band" if bb_pos > 80 else "Middle range"
                summary_parts.append(f"BB Position: {bb_pos:.1f}% ({bb_status})")
            
            return {'summary': ' | '.join(summary_parts)}
            
        except Exception as e:
            return {'summary': f'Summary error: {str(e)}'}

def analyze_stock_for_premarket(symbol: str, kite: Optional[KiteConnect] = None, 
                               benchmark: str = "^NSEI", rs_period: int = 55) -> Dict:
    """
    Comprehensive pre-market technical analysis for a single stock.
    """
    engine = PreMarketTechnicalAnalysisEngine(kite)
    
    # Get comprehensive analysis with custom benchmark and period
    analysis = engine.get_comprehensive_analysis(symbol, benchmark, rs_period)
    
    # Generate trading decision
    decision = engine.generate_trading_decision(analysis)
    
    # Get TradingView link
    tradingview_link = engine.get_tradingview_link(symbol)
    
    # Format summary
    summary = engine.format_technical_summary(analysis)
    
    return {
        'symbol': symbol,
        'analysis': analysis,
        'decision': decision,
        'tradingview_link': tradingview_link,
        'summary': summary,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
