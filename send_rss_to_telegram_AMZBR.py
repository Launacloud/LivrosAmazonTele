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
    try:
        root = ET.fromstring(response_content)
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        print(f"Response content: {response_content}")
        return []
    
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text if item.find('description') is not None else ''
        content = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
        content_html = content.text if content is not None else ''
        image = item.find('{http://search.yahoo.com/mrss/}thumbnail')
        image_url = image.get('url') if image is not None else ''
        items.append({
            'title': title,
            'link': link,
            'description': description,
            'content_html': content_html,
            'image_url': image_url
        })
    return items

def parse_json_feed(response_content):
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Response content: {response_content}")
        return []
    
    items = []
    for item in data.get('items', []):
        title = item.get('title')
        link = item.get('url')  # Adjust the key based on your JSON feed structure
        content_html = item.get('content_html', '')
        image_url = item.get('image')  # Adjust the key based on your JSON feed structure
        items.append({
            'title': title,
            'link': link,
            'content_html': content_html,
            'image_url': image_url
        })
    return items

def parse_rss(feed_url):
    response = requests.get(feed_url)
    if response.status_code != 200:
        print(f"Failed to fetch RSS feed: {response.status_code}")
        return []
    
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        return parse_json_feed(response.content)
    else:
        return parse_xml_feed(response.content)

def fetch_sent_items():
    # Fetch the sent_items.json file from the GitHub repository
    repo_url = "https://raw.githubusercontent.com/Launacloud/LivrosAmazonTele/main/sent_items.json"
    response = requests.get(repo_url)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        print(f"Failed to fetch sent_items.json: {response.status_code}")
        return []

def main():
    # Fetch the sent_items.json file
    sent_items = fetch_sent_items()
    
    rss_items = parse_rss(RSS_FEED_URL)
    if not rss_items:
        print("No RSS items found or failed to parse RSS feed.")
        return
    
    for item in rss_items:
        # Check if the item has been sent before
        if item['link'] in sent_items:
            print(f"Skipping item {item['title']}. Already sent.")
            continue
        
        message = f"<b>{item['title']}</b>\n{item['link']}\n"
        if item['image_url']:
            message += f"<a href='{item['image_url']}'>&#8205;</a>\n"
        if item['content_html']:
            message += f"{item['content_html']}\n"
        response = send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        if response.status_code == 200:
            print(f"Sent message: {message}")
            print(f"RSS Item - Title: {item['title']}, Link: {item['link']}, Image: {item['image_url']}, Content HTML: {item['content_html']}")
            # Add the item link to the sent_items list
            sent_items.append(item['link'])
        else:
            print(f"Failed to send message: {response.status_code}")

    # Save the updated sent_items list back to the sent_items.json file
    with open('sent_items.json', 'w') as file:
        json.dump(sent_items, file)

if __name__ == "__main__":
    main()
