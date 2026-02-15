import requests
import re
from collections import Counter
import time

# User Agent is still required by Reddit to avoid strict rate limiting
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

def get_trending_tickers(subreddits=['wallstreetbets', 'stocks', 'investing', 'valueinvesting'], limit=100):
    """
    Scans subreddits for trending stock tickers using public JSON feeds.
    
    Args:
        subreddits (list): List of subreddit names.
        limit (int): Approximate number of posts to scan (Reddit JSON usually returns 25 per request).
        
    Returns:
        list: A list of tuples (ticker, count).
    """
    ticker_counts = Counter()
    ticker_pattern = re.compile(r'\b[A-Z]{3,5}\b|\$[A-Z]{2,5}')
    blacklist = {
        'I', 'A', 'AND', 'THE', 'FOR', 'IS', 'TO', 'IN', 'OF', 'IT', 'YOU', 'THAT', 'ON', 'WITH', 'ARE', 'WAS', 
        'THIS', 'TEXT', 'POST', 'YOLO', 'DD', 'WSB', 'USA', 'VIEW', 'POLL', 'AM', 'PM', 'EDIT', 'NEW', 'BUY', 
        'SELL', 'HOLD', 'GDP', 'CEO', 'CFO', 'CTO', 'IRA', 'ETF', 'IRS', 'SEC', 'IPO', 'COVID', 'FOMC', 'EPS', 
        'P/E', 'YTD', 'ATH', 'AI', 'EV', 'SAAS', 'ROI', 'FYI', 'KPI', 'ERP', 'ARPU', 'CAGR', 'YOY', 'QOQ'
    }

    for sub in subreddits:
        try:
             # Scan both Hot and New for trending to catch breaking news/memes vs sustained discussions
            urls = [
                f"https://www.reddit.com/r/{sub}/hot.json?limit={min(limit, 100)}",
                f"https://www.reddit.com/r/{sub}/new.json?limit={min(limit, 100)}"
            ]
            
            for url in urls:
                response = requests.get(url, headers=HEADERS)
                
                if response.status_code == 200:
                    data = response.json()
                    children = data.get('data', {}).get('children', [])
                    
                    for post in children:
                        post_data = post['data']
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        
                        text = f"{title} {selftext}"
                        matches = ticker_pattern.findall(text)
                        
                        cleaned_matches = []
                        for m in matches:
                            m = m.replace('$', '')
                            if m not in blacklist:
                                cleaned_matches.append(m)
                        ticker_counts.update(cleaned_matches)
                else:
                    print(f"Error fetching r/{sub}: Status {response.status_code}")
                
               # Be nice to Reddit's servers
                time.sleep(1)
            
        except Exception as e:
            print(f"Error scanning r/{sub}: {e}")

    return ticker_counts.most_common(10)

def get_ticker_discussions(ticker, subreddits=['wallstreetbets', 'stocks', 'investing', 'valueinvesting'], limit=20):
    """
    Fetches posts related to a ticker from the front pages of subreddits.
    Note: Without API, we cannot effectively 'search' history, so we scan Hot/New.
    
    Args:
        ticker (str): Stock ticker to look for.
        
    Returns:
        list: List of dictionaries with post details.
    """
    posts = []
    # Clean ticker for regex matching
    target_ticker = ticker.replace('$', '').upper()
    
    for sub in subreddits:
        try:
            # Check both Hot and New to find relevant recent discussions
            urls = [
                f"https://www.reddit.com/r/{sub}/hot.json?limit=50",
                f"https://www.reddit.com/r/{sub}/new.json?limit=25"
            ]
            
            for url in urls:
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 200:
                    data = response.json()
                    children = data.get('data', {}).get('children', [])
                    
                    for post in children:
                        post_data = post['data']
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        
                        # Check if ticker is in title or body
                        if target_ticker in title.upper() or target_ticker in selftext.upper():
                            posts.append({
                                'title': title,
                                'url': f"https://www.reddit.com{post_data.get('permalink')}",
                                'score': post_data.get('score', 0),
                                'body': selftext,
                                'created': post_data.get('created_utc'),
                                'subreddit': sub
                            })
                            
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error searching r/{sub}: {e}")
            
    # Deduplicate posts based on URL
    unique_posts_dict = {p['url']: p for p in posts}
    unique_posts = list(unique_posts_dict.values())
    
    # Sort by score descending
    unique_posts.sort(key=lambda x: x['score'], reverse=True)
    
    return unique_posts[:limit]
