# Ad Monitor Bot (Avito only)

Telegram bot for monitoring new ads on Avito.

## Features
- Track multiple keywords, cities, and categories
- Set max price and check interval
- Choose browser (Firefox/Chrome) for parsing
- Custom category for Avito

## Setup
1. Create a bot with @BotFather and get token
2. Fill `.env` with your token
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Commands
/start – initialize
/settings – show current settings
/keywords – manage keywords
/cities – manage cities
/category – set Avito category
/price – set max price
/interval – set check interval
/browser – choose browser
/run – start monitoring
/stop – stop monitoring
/status – check status
/help – show help
