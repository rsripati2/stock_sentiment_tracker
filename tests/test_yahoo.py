from clients.yahoo_client import get_yahoo_trending
import json

print("Fetching Yahoo Trending data...")
data = get_yahoo_trending()
print(f"Data type: {type(data)}")
print(f"Data length: {len(data)}")
if data:
    print(f"First item: {data[0]}")
else:
    print("Data is empty.")
