import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')

# Create an empty set for storing sent item titles
SENT_ITEMS_CACHE = set()

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
    # Fetch feed
    response = requests.head(RSS_FEED_URL)  # Send a HEAD request to get the content type
    content_type = response.headers.get('content-type')

    if 'xml' in content_type:
        print("Content Type is XML.")
        feed_items = parse_xml_feed(RSS_FEED_URL)
    elif 'json' in content_type:
        print("Content Type is JSON.")
        feed_items = parse_json_feed(RSS_FEED_URL)
    else:
        print("Unsupported content type.")
        return

    if not feed_items:
        print("No feed items found or failed to parse feeds.")
        return

    # Get new items by comparing with cached items
    new_items = [item for item in feed_items if item['title'] not in SENT_ITEMS_CACHE]

    if not new_items:
        print("No new feed items found since last run.")
        return

    # Send new items
    for item in new_items:
        url = item.get('url') or item.get('link')
        message = f"<b>{item['title']}</b>\n{url}\n{item.get('description', '')}"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        print(f"Sent message: {message}")

    # Update the cache with the titles of the sent items
    SENT_ITEMS_CACHE.update(item['title'] for item in new_items)

if __name__ == "__main__":
    main()
