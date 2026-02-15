from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

def analyze_with_llm(ticker, stock_data, reddit_posts, news_items):
    """
    Uses Gemini to analyze stock data, reddit discussions, and news.
    
    Args:
        ticker (str): Stock ticker symbol.
        stock_data (dict): Market data (price, change, volume).
        reddit_posts (list): List of reddit post dictionaries.
        news_items (list): List of news item dictionaries.
        
    Returns:
        str: The LLM's analysis report.
    """
    if not client:
        return "⚠️ Gemini API Key not found. Please set GEMINI_API_KEY in your .env file."
        
    try:
        # Prepare context for the prompt
        market_context = f"Stock: {ticker}\nPrice: ${stock_data['current_price']}\nChange: {stock_data['change_pct']}%\nVolume: {stock_data['volume']}"
        
        reddit_context = "Reddit Discussions:\n"
        for post in reddit_posts[:5]: # Top 5 posts
            reddit_context += f"- {post['title']} (Score: {post['score']})\n"
            
        news_context = "Recent News:\n"
        for item in news_items[:5]: # Top 5 news
            news_context += f"- {item.get('title', 'No Title')} (Publisher: {item.get('publisher', 'Unknown')})\n"
            
        prompt = f"""
        You are a senior financial analyst and sentiment expert. Analyze the following data for {ticker} and provide a concise, actionable report.
        
        {market_context}
        
        {reddit_context}
        
        {news_context}
        
        Your report should include:
        1. **Sentiment Verdict**: Bullish / Bearish / Neutral (with a confidence score 1-10).
        2. **Key Narratives**: Summarize what investors are talking about (e.g., earnings, rumors, macro factors).
        3. **Risk Factors**: Identify any potential red flags mentioned in news or discussions.
        4. **Trading Signal**: Buy / Sell / Hold / Watch, with a brief reasoning.
        
        Keep it professional, insightful, and under 200 words. Format with Markdown.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        return f"Error generating AI report: {str(e)}"
