def main():
    """Main function to fetch feeds, check for new items, and send them to Telegram."""
    response = requests.head(RSS_FEED_URL)  # Send a HEAD request to get the content type
    content_type = response.headers.get('content-type')
    
    if 'xml' in content_type:
        feed_items = parse_xml_feed(RSS_FEED_URL)
    elif 'json' in content_type:
        feed_items = parse_json_feed(RSS_FEED_URL)
    else:
        print("Unsupported content type.")
        return
    
    if not feed_items:
        print("No feed items found or failed to parse feeds.")
        return
    
    # Get the last run time
    last_run_time = datetime.now()
    
    # Filter new items based on publication time and last run time
    new_items = []
    for item in feed_items:
        pub_date_str = item.get('pub_date', '')
        if pub_date_str:
            try:
                pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
                if pub_date > last_run_time:
                    new_items.append(item)
            except ValueError as e:
                print(f"Error parsing publication date: {e}")
        else:
            print("Publication date is empty for an item.")
    
    if not new_items:
        print("No new feed items found since last run.")
        return
    
    # Send new items
    for item in new_items:
        url = item.get('url') or item.get('link')  # Use 'url' if available, otherwise use 'link'
        message = f"<b>{item['title']}</b>\n{url}\n{item.get('description', '')}"
        send_message(TELEGRAM_BOT_TOKEN, CHAT_ID, message)
        print(f"Sent message: {message}")
