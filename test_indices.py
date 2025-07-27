"""
Test script to check which index symbols are working
"""
# Removed yfinance - using only Zerodha API
import warnings
warnings.filterwarnings('ignore')

# Test different symbol formats for Indian indices
test_symbols = {
    "Nifty 50": ["^NSEI", "NSEI", "^NIFTY", "NIFTY50.NS"],
    "Bank Nifty": ["^NSEBANK", "NSEBANK", "BANKNIFTY.NS"],
    "Sensex": ["^BSESN", "BSESN", "SENSEX.BO"],
    "Nifty Next 50": ["^NSMIDCP", "NSMIDCP", "NIFTYNEXT50.NS"],
    "Nifty 100": ["^CNX100", "CNX100", "NIFTY100.NS"],
    "Nifty 200": ["^CNX200", "CNX200", "NIFTY200.NS"],
    "Nifty 500": ["^CNX500", "CNX500", "NIFTY500.NS"],
    "Nifty Midcap": ["^NSEMDCP50", "NSEMDCP50", "NIFTYMIDCAP.NS"],
    "Nifty Small Cap": ["^CNXSC", "CNXSC", "NIFTYSMALLCAP.NS"],
    "India VIX": ["^INDIAVIX", "INDIAVIX", "INDIAVIX.NS"]
}

def test_symbol(symbol):
    """Test if a symbol works"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d", interval="1d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            return True, price
        else:
            return False, 0
    except:
        return False, 0

print("Testing Indian Index Symbols...")
print("=" * 50)

working_symbols = {}

for index_name, symbols in test_symbols.items():
    print(f"\n{index_name}:")
    found_working = False
    
    for symbol in symbols:
        works, price = test_symbol(symbol)
        status = "✅ WORKS" if works else "❌ FAILED"
        price_str = f"(Price: {price:.2f})" if works else ""
        print(f"  {symbol}: {status} {price_str}")
        
        if works and not found_working:
            working_symbols[index_name] = symbol
            found_working = True

print("\n" + "=" * 50)
print("WORKING SYMBOLS:")
print("=" * 50)

for index_name, symbol in working_symbols.items():
    print(f"{index_name}: {symbol}")

print(f"\nTotal working: {len(working_symbols)}/10")
