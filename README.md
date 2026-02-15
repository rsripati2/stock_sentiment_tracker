# 🚀 Stock Sentiment & News Scanner

A comprehensive tool for tracking market sentiment and trending stocks by aggregating data from Reddit (r/WallStreetBets, etc.), Yahoo Finance, and AI-powered analysis.

## ✨ Features

- **🔥 Social Trends**: Scans Reddit for high-frequency ticker mentions and discussions.
- **📈 Market Momentum**: Fetches real-time trending tickers and gainers from Yahoo Finance.
- **🤖 AI Analyst**: Uses Gemini LLM to generate narrative summaries, risk assessments, and trading signals.
- **📢 Telegram Alerts**: Automated digests sent to your phone with top trending stocks and news.
- **📊 Interactive Dashboard**: Built with Streamlit for a rich, visual analysis experience.

## 🛠 Project Structure

The project is organized into a clean module-based structure:

```text
.
├── app.py                # Main Streamlit dashboard
├── scanner_cli.py        # Command-line interface for scans
├── notify_telegram.py    # Telegram notification service
├── clients/              # External API integrations
│   ├── llm_client.py     # Gemini LLM logic
│   ├── reddit_client.py  # Reddit API integration
│   ├── telegram_client.py# Telegram Bot integration
│   └── yahoo_client.py   # Yahoo Finance data fetching
├── tests/                # Debug and testing scripts
├── requirements.txt      # Project dependencies
└── .env                  # Environment variables (private)
```

## 🚀 Quick Start

### 1. Requirements
Ensure you have Python 3.9+ installed and a virtual environment set up.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory with the following keys:
```ini
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=stock-scanner-1.0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Run the Dashboard
Launch the visual scanner:
```bash
streamlit run app.py
```

### 4. Use the CLI
To analyze a specific stock via terminal:
```bash
python3 scanner_cli.py --mode analyze --ticker AAPL --llm
```

## 🧪 Testing
Run verification tests for the Yahoo client:
```bash
python3 -m tests.test_yahoo
```

## 📄 License
This project is licensed under the MIT License.
