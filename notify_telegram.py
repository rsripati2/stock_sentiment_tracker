import json
from scanner_cli import get_trending_json, analyze_ticker_json
from clients.telegram_client import send_telegram_message
from datetime import datetime

def format_digest(trending_json):
    """Formats the trending JSON into a rich Telegram message with tables."""
    from clients.reddit_client import get_trending_tickers
    from clients.yahoo_client import get_market_news
    
    data = json.loads(trending_json)
    
    reddit_tickers = data.get('reddit_trending', [])[:10]
    yahoo_tickers = data.get('yahoo_trending', [])[:10]
    
    # Get mention counts from Reddit
    reddit_trending_with_counts = get_trending_tickers(limit=50)
    mention_dict = {ticker: count for ticker, count in reddit_trending_with_counts}
    
    msg = f"📊 **Stock Scanner Digest**\n"
    msg += f"🕐 {datetime.now().strftime('%b %d, %Y %I:%M %p')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Reddit Trending Table with Mentions
    msg += "🔥 **REDDIT TRENDING**\n"
    msg += "```\n"
    msg += "Ticker  Price   Chg%  Sent Ment\n"
    msg += "──────────────────────────────\n"
    
    for ticker in reddit_tickers[:8]:
        try:
            analysis_json = analyze_ticker_json(ticker)
            analysis = json.loads(analysis_json)
            
            market = analysis.get('market_data', {})
            sentiment = analysis.get('sentiment', {})
            
            if not market:
                continue
                
            price = market.get('current_price', 0)
            change = market.get('change_pct', 0)
            sent_score = sentiment.get('reddit_score', 0)
            mentions = mention_dict.get(ticker, 0)
            
            # Format price
            if price > 1000:
                price_str = f"{price:.0f}"
            elif price > 10:
                price_str = f"{price:.1f}"
            else:
                price_str = f"{price:.2f}"
            
            # Sentiment emoji
            sent_emoji = "🟢" if sent_score > 0.2 else "🔴" if sent_score < -0.2 else "⚪"
            
            msg += f"{ticker:<6} ${price_str:>5} {change:>5.1f}% {sent_emoji} {mentions:>3}\n"
        except:
            pass
    
    msg += "```\n\n"
    
    # Top 3 Deep Dive
    msg += "🎯 **TOP 3 DEEP DIVE**\n"
    for i, ticker in enumerate(reddit_tickers[:3], 1):
        try:
            analysis_json = analyze_ticker_json(ticker)
            analysis = json.loads(analysis_json)
            
            market = analysis.get('market_data', {})
            sentiment = analysis.get('sentiment', {})
            
            if not market:
                continue
            
            price = market.get('current_price', 0)
            change = market.get('change_pct', 0)
            short_float = market.get('short_float', 0) * 100
            sent_reddit = sentiment.get('reddit_score', 0)
            sent_news = sentiment.get('news_score', 0)
            reddit_posts = sentiment.get('reddit_post_count', 0)
            mentions = mention_dict.get(ticker, 0)
            
            # Change icon
            icon = "🟢" if change >= 0 else "🔴"
            
            msg += f"\n**{i}. {ticker}** {icon}\n"
            msg += f"├ Price: ${price:.2f} ({change:+.2f}%)\n"
            msg += f"├ Mentions: {mentions} | Posts: {reddit_posts}\n"
            msg += f"├ Short Interest: {short_float:.1f}%\n"
            msg += f"├ Reddit Sentiment: {sent_reddit:+.2f}\n"
            msg += f"└ News Sentiment: {sent_news:+.2f}\n"
        except:
            pass
    
    # Yahoo Movers with Details
    msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📈 **YAHOO MOVERS**\n"
    msg += "```\n"
    msg += "Ticker  Price   Change%\n"
    msg += "──────────────────────────\n"
    
    for ticker in yahoo_tickers[:6]:
        try:
            analysis_json = analyze_ticker_json(ticker)
            analysis = json.loads(analysis_json)
            
            market = analysis.get('market_data', {})
            if not market:
                continue
                
            price = market.get('current_price', 0)
            change = market.get('change_pct', 0)
            
            # Format price
            if price > 1000:
                price_str = f"{price:.0f}"
            elif price > 10:
                price_str = f"{price:.1f}"
            else:
                price_str = f"{price:.2f}"
            
            msg += f"{ticker:<6} ${price_str:>6} {change:>6.1f}%\n"
        except:
            pass
    
    msg += "```\n\n"
    
    # Market News
    msg += "📰 **MARKET NEWS**\n"
    try:
        news_items = get_market_news()
        if news_items:
            for i, item in enumerate(news_items[:3], 1):
                title = item.get('title', 'No title')
                link = item.get('link', '')
                # Truncate long titles
                if len(title) > 60:
                    title = title[:57] + "..."
                msg += f"{i}. [{title}]({link})\n"
        else:
            msg += "No recent news available.\n"
    except:
        msg += "Unable to fetch news.\n"
    
    return msg

if __name__ == "__main__":
    print("Generating digest...")
    trending = get_trending_json()
    message = format_digest(trending)
    send_telegram_message(message)
