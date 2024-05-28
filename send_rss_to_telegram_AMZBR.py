import os
import requests
import xml.etree.ElementTree as ET
import json
import logging

# Set up logging to a file
logging.basicConfig(filename='rss_to_telegram.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN_AMZBR')
RSS_FEED_URL = os.getenv('RSS_FEED_URLAMZBR')
CHAT_ID = os.getenv('TELEGRAM_CHAT_IDAMZBR')
SENT_ITEMS_FILE = os.path.join(os.path.dirname(__file__), 'sent_items.json')

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
    try:
        root = ET.fromstring(response_content)
        logging.debug("Successfully parsed XML feed.")
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML: {e}")
        logging.debug(f"Response content: {response_content}")
        return []
    
    items = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
        content_html = entry.find('{http://www.w3.org/2005/Atom}content').text
        image_url = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
        item_id = entry.find('{http://www.w3.org/2005/Atom}id').text
        logging.debug(f"Parsed item - ID: {item_id}, Title: {title}")
        items.append({
            'id': item_id,
            'title': title,
            'link': link,
            'content_html': content_html,
            'image_url': image_url
        })
    return items

def parse_json_feed(response_content):
    try:
        data = json.loads(response_content)
        logging.debug("Successfully parsed JSON feed.")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        logging.debug(f"Response content: {response_content}")
        return []
    
    items = []
    for item in data.get('items', []):
        title = item.get('title')
        link = item.get('url')  # Adjust the key based on your JSON feed structure
        content_html = item.get('content_html', '')
        image_url = item.get('image')  # Adjust the key based on your JSON feed structure
        item_id = item.get('id')  # Adjust the key based on your JSON feed structure
        logging.debug(f"Parsed item - ID: {item_id}, Title: {title}")
        items.append({
            'id': item_id,
            'title': title,
            'link': link,
            'content_html': content_html,
            'image_url': image_url
        })
    return items

def parse_rss(feed_url):
    logging.debug(f"Fetching RSS feed from: {feed_url}")
    response = requests.get(feed_url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch RSS feed: {response.status_code}")
        return []
    
    content_type = response.headers.get('Content-Type', '')
    logging.debug(f"Content type: {content_type}")
    if 'application/json' in content_type:
        logging.debug("Detected JSON format.")
        return parse_json_feed(response.content)
    else:
        logging.debug("Detected XML format.")
        return parse_xml_feed(response.content)

def load_sent_items():
    if not os.path.exists(SENT_ITEMS_FILE):
        logging.debug("Sent items file not found. Creating new one.")
        return set()
    
    with open(SENT_ITEMS_FILE, 'r') as f:
        logging.debug("Loading sent items from file.")
        return set(json.load(f))

def save_sent_items(sent_items):
    with open(SENT_ITEMS_FILE, 'w') as f:
        logging.debug("Saving sent items to file.")
        json.dump(list(sent_items), f)

def main():
    sent_items = load_sent_items()
    logging.debug(f"Loaded sent items: {sent_items}")
    rss_items = parse_rss(RSS_FEED_URL)
    if not rss_items:
        logging.debug("No RSS items found or failed to parse RSS feed.")
        return
    
    new_sent_items = set()
    for item in rss_items:
        if item['id'] in sent_items:
            logging.debug(f"Item already sent - ID: {item['id']}, Title: {item['title']}")
            continue
        
        message = f"<b>{item['title']}</b>\n{item['link']}\n"
        if item['image_url']:
            message += f"<a href='{item['image_url']}'>&#8205;</a>\n"
        if item['content_html']:
            message += f"{item['content_html']}\n"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        logging.debug(f"Sent message: {message}")
        logging.debug(f"RSS Item - Title: {item['title']}, Link: {item['link']}, Image: {item['image_url']}, Content HTML: {item['content_html']}")
        new_sent_items.add(item['id'])
    
    sent_items.update(new_sent_items)
    save_sent_items(sent_items)
    logging.debug(f"Updated sent items: {sent_items}")

if __name__ == "__main__":
    main()
