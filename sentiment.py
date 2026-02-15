from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_text(text):
    """
    Analyzes the sentiment of a given text using VADER.
    
    Args:
        text (str): The text to analyze.
        
    Returns:
        dict: A dictionary containing the compound, pos, neu, and neg scores.
    """
    if not text:
        return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
    
    scores = analyzer.polarity_scores(text)
    return scores

def generate_signal(sentiment_score, mention_volume, price_trend_pct=0):
    """
    Generates a trading signal based on sentiment, volume, and price trend.
    
    Args:
        sentiment_score (float): The compound sentiment score (-1 to 1).
        mention_volume (int): The number of mentions or relative volume.
        price_trend_pct (float): Recent price change percentage.
        
    Returns:
        str: 'STRONG BUY', 'BUY', 'WATCH', 'AVOID', 'SELL'
    """
    # Simple logic for demonstration
    if sentiment_score > 0.2 and mention_volume > 10:
        if price_trend_pct > 0:
            return "STRONG BUY"
        return "BUY"
    elif sentiment_score < -0.2 and mention_volume > 10:
        return "SELL"
    elif sentiment_score < -0.05:
        return "AVOID"
    else:
        return "WATCH"
