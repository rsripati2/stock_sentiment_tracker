import requests
import json

url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

print(f"Fetching {url}...")
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    print("Response Content Preview:", response.text[:500])
    
    if response.status_code == 200:
        data = response.json()
        result = data.get('finance', {}).get('result', [])
        print(f"Result length: {len(result)}")
        if result:
            quotes = result[0].get('quotes', [])
            print(f"Quotes length: {len(quotes)}")
            print(quotes)
        else:
            print("No 'result' found in 'finance' object.")
    else:
        print("Request failed.")
except Exception as e:
    print(f"Error: {e}")
