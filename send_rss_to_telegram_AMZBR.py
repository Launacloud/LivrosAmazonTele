import os
import requests
import feedparser
import json

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')
CACHE_FILE = 'sent_messages_cache.json'

# Function to send a message to a Telegram chat
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Error sending message: {response.text}")

# Function to load sent message IDs from cache
def load_sent_message_ids():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return []

# Function to save sent message IDs to cache
def save_sent_message_ids(sent_message_ids):
    with open(CACHE_FILE, 'w') as f:
        json.dump(sent_message_ids, f)

# Function to parse the RSS feed and send new entries to Telegram
def send_rss_to_telegram():
    feed = feedparser.parse(RSS_FEED_URL)
    sent_message_ids = load_sent_message_ids()
    new_sent_message_ids = []

    for entry in feed.entries:
        entry_id = entry.id
        if entry_id not in sent_message_ids:
            title = entry.title
            link = entry.link
            message = f"<b>{title}</b>\n{link}"
            send_telegram_message(message)
            new_sent_message_ids.append(entry_id)
            # To avoid sending too many messages at once, we can break after sending a few messages.
            if len(new_sent_message_ids) >= 20:
                break

    # Update the cache with the new sent message IDs
    save_sent_message_ids(sent_message_ids + new_sent_message_ids)

if __name__ == "__main__":
    send_rss_to_telegram()
