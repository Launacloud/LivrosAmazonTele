import os
import requests
import xml.etree.ElementTree as ET
import json

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
SENT_ITEMS_FILE = 'sent_items.json'  # Path to the sent items file

def send_message(bot_token, chat_id, text):
    # Function to send message to Telegram
    # Implementation omitted for brevity
    pass

def parse_xml_feed(response_content):
    # Function to parse XML feed
    # Implementation omitted for brevity
    pass

def parse_rss(feed_url):
    # Function to parse RSS feed
    # Implementation omitted for brevity
    pass

def fetch_sent_items():
    # Function to fetch sent items from the sent_items.json file
    if os.path.exists(SENT_ITEMS_FILE):
        with open(SENT_ITEMS_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Failed to parse sent items JSON: {e}")
    return []

def save_sent_items(sent_items):
    # Function to save sent items to the sent_items.json file
    with open(SENT_ITEMS_FILE, 'w') as file:
        json.dump(sent_items, file, indent=4)

def main():
    # Fetch sent items
    sent_items = fetch_sent_items()

    # Parse RSS feed
    rss_items = parse_rss(RSS_FEED_URL)

    if not rss_items:
        print("No RSS items found or failed to parse RSS feed.")
        return

    for item in rss_items:
        # Check if item is already sent
        if item in sent_items:
            print(f"Skipping already sent item: {item}")
            continue

        # Send message
        message = f"<b>{item['title']}</b>\n{item['link']}\n"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        print(f"Sent message: {message}")

        # Add item to sent items
        sent_items.append(item)

    # Save sent items
    save_sent_items(sent_items)

if __name__ == "__main__":
    main()
