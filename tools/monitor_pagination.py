
import sys
import os
import time

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from market_data_api import get_ohlcv_data

def run_monitor():
    token = "ETH"
    timeframe = "15m"
    days = 365
    
    # Calculate expected candles
    expected = days * 24 * 4 # 15m = 96 per day
    print(f"Goal: Fetch {days} days of {timeframe} for {token} => ~{expected} candles")
    
    start_time = time.time()
    try:
        data = get_ohlcv_data(token, timeframe, limit=expected)
        elapsed = time.time() - start_time
        
        count = len(data)
        print(f"Result: Received {count} candles in {elapsed:.2f}s")
        
        if count > 0:
            first = data[0]['time']
            last = data[-1]['time']
            print(f"Range: {first} -> {last}")
            
        if count < expected * 0.9:
            print("❌ FAILURE: Received significantly fewer candles than expected.")
        else:
            print("✅ SUCCESS: Pagination working correctly.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_monitor()
