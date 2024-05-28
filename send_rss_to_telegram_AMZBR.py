import os
import requests
import xml.etree.ElementTree as ET
import json

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')

def send_message(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response

def parse_xml_feed(response_content):
    # Your parsing code goes here

def parse_json_feed(response_content):
    # Your parsing code goes here

def parse_rss(feed_url):
    # Your parsing code goes here

def fetch_sent_items():
    sent_items_file = 'sent_items.json'
    if not os.path.exists(sent_items_file):
        # Create the file if it doesn't exist
        with open(sent_items_file, 'w') as f:
            json.dump([], f)
            print("Sent items file created successfully.")
    
    # Read the sent items from the file
    with open(sent_items_file, 'r') as f:
        return json.load(f)

def save_sent_item(item):
    sent_items = fetch_sent_items()
    sent_items.append(item)
    with open('sent_items.json', 'w') as f:
        json.dump(sent_items, f)

def main():
    rss_items = parse_rss(RSS_FEED_URL)
    if not rss_items:
        print("No RSS items found or failed to parse RSS feed.")
        return
    
    sent_items = fetch_sent_items()
    for item in rss_items:
        if item not in sent_items:
            message = f"<b>{item['title']}</b>\n{item['link']}\n"
            if item['image_url']:
                message += f"<a href='{item['image_url']}'>&#8205;</a>\n"
            if item['content_html']:
                message += f"{item['content_html']}\n"
            response = send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
            if response.status_code == 200:
                save_sent_item(item)
                print(f"Sent message: {message}")
                print(f"RSS Item - Title: {item['title']}, Link: {item['link']}, Image: {item['image_url']}, Content HTML: {item['content_html']}")
            else:
                print(f"Failed to send message: {response.status_code}")

if __name__ == "__main__":
    main()
