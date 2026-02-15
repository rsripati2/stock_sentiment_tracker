import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    print("❌ TELEGRAM_BOT_TOKEN not found in .env")
    exit(1)

url = f"https://api.telegram.org/bot{token}/getUpdates"

try:
    response = requests.get(url)
    data = response.json()
    
    if data.get('ok') and data.get('result'):
        print("✅ Recent messages to your bot:\n")
        for update in data['result'][-5:]:  # Last 5 messages
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                username = update['message']['chat'].get('username', 'N/A')
                first_name = update['message']['chat'].get('first_name', 'N/A')
                print(f"Chat ID: {chat_id}")
                print(f"Name: {first_name}")
                print(f"Username: @{username}")
                print("---")
        
        print("\n💡 Use one of these Chat IDs in your .env file")
    else:
        print("⚠️ No messages found. Please:")
        print("1. Open Telegram")
        print("2. Search for your bot: @sr19_bot")
        print("3. Send it any message (e.g., 'hello')")
        print("4. Run this script again")
        
except Exception as e:
    print(f"❌ Error: {e}")
