import streamlit as st
import pandas as pd
import warnings
from clients.reddit_client import get_trending_tickers, get_ticker_discussions
from clients.yahoo_client import get_stock_news, get_stock_data, get_yahoo_trending, get_market_news
from sentiment import analyze_text, generate_signal

# Suppress SSL warnings from urllib3
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')

# Page Config
st.set_page_config(page_title="Stock Sentiment Scanner", layout="wide")

# Title
st.title("🚀 Stock Sentiment & News Scanner")

# Sidebar
st.sidebar.header("Configuration")
ticker_input = st.sidebar.text_input("Search Ticker (e.g., AAPL)", "").upper()

# Main Analysis Logic (Top Priority if User Searches)
if ticker_input:
    st.header(f"🔎 Analysis for: {ticker_input}")
    
    # --- AI ANALYST SECTION ---
    st.subheader("🤖 AI Analyst Insight")
    if st.button(f"Generate AI Report for {ticker_input}"):
        with st.spinner("Consulting Gemini AI Analyst..."):
            try:
                from clients.llm_client import analyze_with_llm
                # Re-fetch data for the LLM to ensure it has latest context
                # (We could optimize by passing data if already fetched, but for now this is cleaner)
                llm_stock = get_stock_data(ticker_input, extended_info=True)
                llm_reddit = get_ticker_discussions(ticker_input, limit=10)
                llm_news = get_stock_news(ticker_input)
                
                if llm_stock:
                    report = analyze_with_llm(ticker_input, llm_stock, llm_reddit, llm_news)
                    st.markdown(report)
                else:
                    st.error("Could not fetch stock data for analysis.")
            except Exception as e:
                st.error(f"AI Module Error: {e}")
    st.markdown("---")

    # 1. Market Data
    market_col, signal_col = st.columns(2)
    
    with market_col:
        st.subheader("Market Data")
        stock_data = get_stock_data(ticker_input)
        if stock_data:
            st.metric("Current Price", f"${stock_data['current_price']:.2f}", f"{stock_data['change_pct']:.2f}%")
            st.metric("Volume", f"{stock_data['volume']:,}")
        else:
            st.error("Could not fetch market data. Ticker might be invalid.")
            
    # 2. Reddit Analysis, 3. News, 4. Signal
    # Let's put these in columns or tabs inside the analysis section too? 
    # For now, keeping them stacked as per original design but compacted
    
    # 2. Reddit Analysis
    st.subheader("Reddit Sentiment")
    reddit_posts = get_ticker_discussions(ticker_input, limit=20)
    
    if reddit_posts:
        reddit_scores = []
        for post in reddit_posts:
            sentiment = analyze_text(f"{post['title']} {post['body']}")
            reddit_scores.append(sentiment['compound'])
            
        avg_reddit_sentiment = sum(reddit_scores) / len(reddit_scores) if reddit_scores else 0
        st.metric("Avg Reddit Sentiment", f"{avg_reddit_sentiment:.2f}")
        
        with st.expander("Recent Reddit Discussions"):
            for post in reddit_posts:
                st.markdown(f"**[{post['title']}]({post['url']})**")
                st.caption(f"Score: {post['score']} | Subreddit: r/{post['subreddit']}")
                st.write(post['body'][:200] + "..." if len(post['body']) > 200 else post['body'])
                st.markdown("---")
    else:
        st.info("No recent Reddit discussions found for this ticker.")
        avg_reddit_sentiment = 0

    # 3. News Analysis
    st.subheader("News Sentiment")
    news_items = get_stock_news(ticker_input)
    
    if news_items:
        news_scores = []
        for item in news_items:
            title = item.get('title', '')
            if title:
                sentiment = analyze_text(title)
                news_scores.append(sentiment['compound'])
                
        avg_news_sentiment = sum(news_scores) / len(news_scores) if news_scores else 0
        st.metric("Avg News Sentiment", f"{avg_news_sentiment:.2f}")
        
        with st.expander("Recent News"):
            for item in news_items:
                st.markdown(f"**[{item.get('title', 'No Title')}]({item.get('link', '#')})**")
                pub_time = item.get('providerPublishTime', 0)
                if pub_time:
                    from datetime import datetime
                    dt_object = datetime.fromtimestamp(pub_time)
                    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                    st.caption(f"Publisher: {item.get('publisher', 'Unknown')} | {formatted_time}")
                else:
                    st.caption(f"Publisher: {item.get('publisher', 'Unknown')}")
                st.markdown("---")
    else:
        st.info("No recent news found for this ticker.")
        avg_news_sentiment = 0

    # 4. Trading Signal
    with signal_col:
        st.subheader("Trading Signal")
        overall_sentiment = (avg_reddit_sentiment + avg_news_sentiment) / 2
        mention_volume = len(reddit_posts) if reddit_posts else 0
        price_trend = stock_data['change_pct'] if stock_data else 0
        
        signal = generate_signal(overall_sentiment, mention_volume, price_trend)
        
        if signal == "STRONG BUY":
            st.success(f"Signal: **{signal}** 🚀")
        elif signal == "BUY":
            st.success(f"Signal: **{signal}** 🟢")
        elif signal == "SELL":
            st.error(f"Signal: **{signal}** 🔴")
        elif signal == "AVOID":
            st.warning(f"Signal: **{signal}** ⚠️")
        else:
            st.info(f"Signal: **{signal}** 👀")
            
        st.caption(f"Based on Sentiment: {overall_sentiment:.2f} | Mentions: {mention_volume} | Trend: {price_trend:.2f}%")

    st.markdown("---")

# DASHBOARD TABS
st.header("📊 Market Overview")
tab_reddit, tab_squeeze, tab_yahoo, tab_news = st.tabs(["🔥 Reddit Trends", "🚀 Potential Squeezes", "📈 Yahoo Trends", "📢 Major News"])

# Fetch shared data
trending_tickers = []
try:
    trending_tickers = get_trending_tickers()
except Exception as e:
    st.error(f"Error serving Reddit trends: {e}")

# --- TAB 1: REDDIT TRENDS ---
with tab_reddit:
    st.header("🔥 Trending on Reddit")
    if trending_tickers:
        data = []
        for ticker, mentions in trending_tickers[:10]:
            stock_data = get_stock_data(ticker)
            price = "N/A"
            trend = "N/A"
            prev_close = "N/A"
            
            if stock_data:
                price = f"${stock_data['current_price']:.2f}"
                change = stock_data['change_pct']
                if stock_data['current_price'] and change is not None:
                        prev_close_val = stock_data['current_price'] / (1 + (change/100))
                        prev_close = f"${prev_close_val:.2f}"
                
                if change > 0:
                    trend = f"🟢 +{change:.2f}% 📈"
                elif change < 0:
                    trend = f"🔴 {change:.2f}% 📉"
                else:
                    trend = "⚪ 0.00%"
            
            data.append({
                "Ticker": ticker,
                "Mentions": mentions,
                "Price": price,
                "Prev Close": prev_close,
                "Trend": trend
            })
            
        st.dataframe(pd.DataFrame(data), height=400, hide_index=True)
    else:
        st.warning("No trending tickers found. Reddit might be rate-limiting traffic.")

# --- TAB 2: SQUEEZE DETECTOR ---
with tab_squeeze:
    st.header("🚀 Potential Squeezes & High Activity")
    st.caption("Score based on: Reddit Mentions + Volume Spike + Short Interest")

    if trending_tickers:
        squeeze_data = []
        with st.spinner("Analyzing top tickers..."):
            for ticker, mentions in trending_tickers[:10]:
                data = get_stock_data(ticker, extended_info=True)
                if data:
                    short_float = data.get('short_float', 0)
                    if short_float is None: short_float = 0
                    
                    avg_vol = data.get('avg_volume', 1)
                    curr_vol = data.get('volume', 0)
                    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 0
                    
                    score = (mentions / 10)
                    if short_float > 0.20: score *= 2.0
                    elif short_float > 0.10: score *= 1.5
                    
                    if vol_ratio > 1.5: score *= 1.5
                    
                    squeeze_data.append({
                        "Ticker": ticker,
                        "Squeeze Score": round(score, 1),
                        "Short Interest": f"{short_float*100:.1f}%" if short_float else "N/A",
                        "Vol/Avg": f"{vol_ratio:.1f}x",
                        "Mentions": mentions,
                        "Price": f"${data['current_price']:.2f}"
                    })
        
        if squeeze_data:
            df_squeeze = pd.DataFrame(squeeze_data).sort_values(by="Squeeze Score", ascending=False)
            st.dataframe(df_squeeze, height=300, hide_index=True)
        else:
            st.info("No squeeze candidates found having extended data.")
    else:
         st.warning("No data available for analysis.")

# --- TAB 3: YAHOO TRENDS ---
with tab_yahoo:
    st.header("📈 Trending on Yahoo Finance")
    try:
        yahoo_trending = get_yahoo_trending()
        if yahoo_trending:
            y_data = []
            for item in yahoo_trending[:10]:
                ticker = item.get('symbol')
                stock_data = get_stock_data(ticker)
                price = "N/A"
                trend = "N/A"
                prev_close = "N/A"

                if stock_data:
                    price = f"${stock_data['current_price']:.2f}"
                    change = stock_data['change_pct']
                    if stock_data['current_price'] and change is not None:
                        prev_close_val = stock_data['current_price'] / (1 + (change/100))
                        prev_close = f"${prev_close_val:.2f}"
                    
                    if change > 0:
                        trend = f"🟢 +{change:.2f}% 📈"
                    elif change < 0:
                        trend = f"🔴 {change:.2f}% 📉"
                    else:
                        trend = "⚪ 0.00%"
                
                y_data.append({
                    "Ticker": ticker,
                    "Price": price,
                    "Prev Close": prev_close,
                    "Trend": trend
                })
            st.dataframe(pd.DataFrame(y_data), height=400, hide_index=True)
        else:
            st.info("No trending data returned from Yahoo Finance.")
    except Exception as e:
        st.error(f"Error fetching Yahoo trending: {e}")

# --- TAB 4: MARKET NEWS ---
with tab_news:
    st.header("📢 Major Market News")
    try:
        market_news = get_market_news()
        if market_news:
            for item in market_news[:10]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### [{item.get('title', 'No Title')}]({item.get('link', '#')})")
                    pub_time = item.get('providerPublishTime', 0)
                    time_str = ""
                    if pub_time:
                        from datetime import datetime
                        dt_object = datetime.fromtimestamp(pub_time)
                        time_str = dt_object.strftime('%Y-%m-%d %H:%M')
                    st.caption(f"Source: {item.get('publisher', 'Unknown')} | {time_str}")
                with col2:
                    title = item.get('title', '')
                    if title:
                        s = analyze_text(title)
                        score = s['compound']
                        if score > 0.05:
                            st.markdown(f"**Sentiment:** 🟢 {score:.2f}")
                        elif score < -0.05:
                            st.markdown(f"**Sentiment:** 🔴 {score:.2f}")
                        else:
                            st.markdown(f"**Sentiment:** ⚪ {score:.2f}")
                st.markdown("---")
        else:
            st.info("No market news found at the moment.")
    except Exception as e:
        st.error(f"Error fetching market news: {e}")
