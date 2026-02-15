import argparse
import json
import sys
from clients.reddit_client import get_trending_tickers, get_ticker_discussions
from clients.yahoo_client import get_stock_data, get_stock_news, get_yahoo_trending
from clients.llm_client import analyze_with_llm
from sentiment import analyze_text

def get_trending_json():
    """Scans for trending tickers and returns JSON."""
    try:
        # Get Reddit Trends
        reddit_trends = get_trending_tickers(limit=50) # Increased limit for CLI
        
        # Get Yahoo Trends
        yahoo_trends_raw = get_yahoo_trending()
        yahoo_trends = []
        for item in yahoo_trends_raw:
             yahoo_trends.append(item.get('symbol'))

        return json.dumps({
            "source": "StockSentimentScanner",
            "type": "trending",
            "reddit_trending": [t[0] for t in reddit_trends], # Just list of tickers
            "yahoo_trending": yahoo_trends
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

def analyze_ticker_json(ticker, use_llm=False):
    """Analyzes a single ticker and returns JSON."""
    try:
        # 1. Market Data
        stock_data = get_stock_data(ticker, extended_info=True)
        
        # 2. Reddit Data
        reddit_posts = get_ticker_discussions(ticker, limit=10)
        reddit_sentiment_score = 0
        if reddit_posts:
            scores = [analyze_text(p['title'] + " " + p['body'])['compound'] for p in reddit_posts]
            reddit_sentiment_score = sum(scores) / len(scores)

        # 3. News Data
        news_items = get_stock_news(ticker)
        news_sentiment_score = 0
        if news_items:
            # Handle potential missing title
            titles = [item.get('title', '') for item in news_items if item.get('title')]
            if titles:
                scores = [analyze_text(t)['compound'] for t in titles]
                news_sentiment_score = sum(scores) / len(scores)

        # 4. LLM Analysis
        llm_report = None
        if use_llm and stock_data:
            llm_report = analyze_with_llm(ticker, stock_data, reddit_posts, news_items)

        result = {
            "ticker": ticker,
            "market_data": stock_data,
            "sentiment": {
                "reddit_score": round(reddit_sentiment_score, 2),
                "news_score": round(news_sentiment_score, 2),
                "reddit_post_count": len(reddit_posts),
                "news_item_count": len(news_items)
            },
            "llm_report": llm_report
        }
        return json.dumps(result, indent=2)
        
    except Exception as e:
         return json.dumps({"error": str(e), "ticker": ticker})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stock Sentiment Scanner CLI")
    parser.add_argument("--mode", choices=["trending", "analyze"], required=True, help="Action to perform")
    parser.add_argument("--ticker", help="Ticker symbol (required for analyze mode)")
    parser.add_argument("--llm", action="store_true", help="Enable LLM analysis (consumes API quota)")
    
    args = parser.parse_args()
    
    if args.mode == "trending":
        print(get_trending_json())
    elif args.mode == "analyze":
        if not args.ticker:
            print(json.dumps({"error": "--ticker is required for analyze mode"}))
            sys.exit(1)
        print(analyze_ticker_json(args.ticker.upper(), args.llm))
