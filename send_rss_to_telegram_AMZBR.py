import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')

def send_message(bot_token, chat_id, text):
    """Send a message to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response

def parse_feed(feed_url):
    """Parse the XML feed and return new items."""
    response = requests.get(feed_url)
    if response.status_code != 200:
        print(f"Failed to fetch feed: {response.status_code}")
        return []
    
    root = ET.fromstring(response.content)
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text if item.find('link') is not None else ''
        description = item.find('description').text if item.find('description') is not None else ''
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
        items.append({
            'title': title,
            'link': link,
            'description': description,
            'pub_date': pub_date
        })
    return items

def main():
    """Main function to fetch feed, check for new items, and send them to Telegram."""
    # Fetch feed
    feed_items = parse_feed(RSS_FEED_URL)
    if not feed_items:
        print("No feed items found or failed to parse feed.")
        return
    
    # Get the last run time
    last_run_time = datetime.now()
    
    # Filter new items based on publication time and last run time
    new_items = [item for item in feed_items if datetime.strptime(item['pub_date'], '%a, %d %b %Y %H:%M:%S %z') > last_run_time]
    if not new_items:
        print("No new feed items found since last run.")
        return
    
    # Send new items
    for item in new_items:
        url = item.get('url') or item.get('link')  # Use 'url' if available, otherwise use 'link'
        message = f"<b>{item['title']}</b>\n{url}\n{item.get('description', '')}"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        print(f"Sent message: {message}")

if __name__ == "__main__":
    main()
