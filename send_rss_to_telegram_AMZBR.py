import os
import requests
import json
import xml.etree.ElementTree as ET

# Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')

# Define the path to the cache file
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

def parse_xml_feed(feed_url):
    """Parse the XML feed and return new items."""
    response = requests.get(feed_url)
    if response.status_code != 200:
        print(f"Failed to fetch XML feed: {response.status_code}")
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

def parse_json_feed(feed_url):
    """Parse the JSON feed and return new items."""
    response = requests.get(feed_url)
    if response.status_code != 200:
        print(f"Failed to fetch JSON feed: {response.status_code}")
        return []

    feed_data = response.json()
    items = []
    for entry in feed_data.get('items', []):
        title = entry.get('title', '')
        link = entry.get('link', '')  # Default to empty string if 'link' is not present
        if 'link' not in entry:  # Check if 'link' is not present
            link = entry.get('url', '')  # Assign the value of 'url' to 'link' if 'link' is not present
        description = entry.get('description', '')
        pub_date = entry.get('pub_date', '')
        items.append({
            'title': title,
            'link': link,
            'description': description,
            'pub_date': pub_date
        })
    return items

def main():
    """Main function to fetch feeds, check for new items, and send them to Telegram."""
    # Load cache
    cached_data = set()
    # Attempt to restore cache
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, 'r') as cache_file:
            try:
                cached_data = {tuple(item.items()) for item in json.load(cache_file)}
                print("Cache loaded successfully.")
            except json.JSONDecodeError:
                print("Error decoding cache file. Skipping cache loading.")
    else:
        print("No cache file found.")

    # Print cache file contents
    if cached_data:
        print("Cache file contents:")
        for item in cached_data:
            print(item)
    else:
        print("Cache is empty.")

    # Fetch feed
    response = requests.head(RSS_FEED_URL)  # Send a HEAD request to get the content type
    content_type = response.headers.get('co
