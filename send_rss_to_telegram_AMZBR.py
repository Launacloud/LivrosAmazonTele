import os
import requests
import json
import xml.etree.ElementTree as ET

# Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')

# Cache file path
CACHE_FILE_PATH = './sent_items_cache.json'

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

def parse_rss(feed_url):
    """Parse the RSS feed and return new items."""
    response = requests.get(feed_url)
    if response.status_code != 200:
        print(f"Failed to fetch RSS feed: {response.status_code}")
        return []

    try:
        feed_data = response.json()
        items = feed_data.get('items', [])
        return items
    except json.JSONDecodeError:
        try:
            root = ET.fromstring(response.content)
            items = []
            for item in root.findall('.//item'):
                title = item.find('title').text
                link = item.find('link').text if item.find('link') is not None else ''
                description = item.find('description').text if item.find('description') is not None else ''
                items.append({
                    'title': title,
                    'link': link,
                    'description': description
                })
            return items
        except ET.ParseError as e:
            print(f"Failed to parse XML response: {e}")
            print(f"Response content: {response.content}")
            return []

def load_cache(cache_file):
    """Load the cache file if it exists."""
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return []

def save_cache(cache_file, items):
    """Save the items to the cache file."""
    with open(cache_file, 'w') as f:
        json.dump(items, f, indent=4)

def main():
    """Main function to fetch RSS feed, check cache, and send new items to Telegram."""
    # Fetch RSS feed
    rss_items = parse_rss(RSS_FEED_URL)
    if not rss_items:
        print("No RSS items found or failed to parse RSS feed.")
        return
    
    # Load cache
    cache = load_cache(CACHE_FILE_PATH)
    
    # Filter new items
    new_items = [item for item in rss_items if item not in cache]
    if not new_items:
        print("No new RSS items found.")
        return
    
    # Send new items
    for item in new_items:
        message = f"<b>{item['title']}</b>\n{item.get('link', '')}\n{item.get('description', '')}"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        print(f"Sent message: {message}")
    
    # Update cache with new items
    cache.extend(new_items)
    save_cache(CACHE_FILE_PATH, cache)

if __name__ == "__main__":
    main()
