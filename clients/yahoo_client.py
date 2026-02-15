import yfinance as yf
import pandas as pd

def get_stock_news(ticker):
    """
    Fetches the latest news for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL').
        
    Returns:
        list: A list of dictionaries containing news items, sorted by time.
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        # Sort by publication time descending (newest first)
        if news:
            news.sort(key=lambda x: x.get('providerPublishTime', 0), reverse=True)
        return news
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []

def get_stock_data(ticker, extended_info=False):
    """
    Fetches real-time market data for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol.
        extended_info (bool): Whether to fetch slower, extended data like Short Interest.
        
    Returns:
        dict: A dictionary containing market data.
    """
    try:
        stock = yf.Ticker(ticker)
        # fast_info is often faster for real-time data
        info = stock.fast_info
        
        try:
            # Check if fast_info has data, sometimes it might be empty or raise error
            # Accessing .last_price can trigger a KeyError or 'currentTradingPeriod' error if data is missing
            if not info or not hasattr(info, 'last_price'):
                 return None
    
            current_price = info.last_price
            prev_close = info.previous_close
            
            # Ensure we have valid numbers
            if current_price is None:
                return None
                
            if prev_close and prev_close != 0:
                change_pct = ((current_price - prev_close) / prev_close) * 100
            else:
                change_pct = 0.0
                
            volume = info.last_volume if info.last_volume is not None else 0
            
            data = {
                'current_price': float(current_price),
                'change_pct': float(change_pct),
                'volume': int(volume),
                'currency': info.currency
            }
        except (KeyError, TypeError, OSError) as e:
            # Catch known yfinance errors (e.g. 'currentTradingPeriod')
            # returning None will just skip this ticker in the UI
            return None
        
        if extended_info:
            try:
                # stock.info is slower but contains detailed stats
                full_info = stock.info
                data['short_float'] = full_info.get('shortPercentOfFloat', 0)
                data['avg_volume'] = full_info.get('averageVolume', 0)
                data['market_cap'] = full_info.get('marketCap', 0)
            except Exception as e:
                print(f"Error fetching extended info for {ticker}: {e}")
                data['short_float'] = 0
                data['avg_volume'] = 0

        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_yahoo_trending():
    """
    Fetches trending stocks from Yahoo Finance.
    
    Returns:
        list: A list of dicts with 'symbol' and other metadata.
    """
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
        # Yahoo requires a User-Agent and other headers to avoid 429s
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        import requests
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('finance', {}).get('result', [])
            if result:
                raw_quotes = result[0].get('quotes', [])
                # Filter out Crypto (usually ends in -USD, -EUR, etc. or =X for currencies)
                stocks_only = []
                for q in raw_quotes:
                    symbol = q.get('symbol', '')
                    # Heuristic: exclude typical crypto pairs and forex
                    if not (symbol.endswith('-USD') or symbol.endswith('-CAD') or 
                            symbol.endswith('-EUR') or symbol.endswith('=X')):
                        stocks_only.append(q)
                return stocks_only
        return []
    except Exception as e:
        print(f"Error fetching Yahoo trending: {e}")
        return []

def get_market_news():
    """
    Fetches general market news using yahooquery (more reliable for search/news).
    
    Returns:
        list: News items.
    """
    try:
        from yahooquery import search
        # Search for "market" or "stocks" to get general news
        result = search("market news")
        if result and 'news' in result:
             return result['news']
        return []
    except Exception as e:
        print(f"Error fetching market news: {e}")
        return []
