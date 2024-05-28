name: RSS to Telegram Workflow

on:
  schedule:
    - cron: '*/15 * * * *'  # Runs every 15 minutes
  workflow_dispatch:
  push:

jobs:
  send_rss_to_telegram:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests  # Install the requests module

      - name: Check if cache directory exists
        run: |
          if [ ! -d ./cache ]; then
            mkdir -p ./cache
            echo "Cache directory created."
          fi

      - name: Check if cache file exists
        run: |
          if [ -f ./cache/sent_items.json ]; then
            echo "Cache file exists."
            python send_rss_to_telegram.py --cache ./cache/sent_items.json
          else
            echo "Cache file does not exist. Skipping script execution."
          fi

      - name: Run script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          RSS_FEED_URL: ${{ secrets.RSS_FEED_URL }}
        run: |
          cd $GITHUB_WORKSPACE  # Navigate to the root directory of the repository
          python send_rss_to_telegram.py

  install_triggers:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Use Node.js 14.x
        uses: actions/setup-node@v2
        with:
          node-version: '14.x'

      - name: Install dependencies
        run: |
          npm install
          npm install @actionsflow/trigger-schedule
