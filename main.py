# Telegram Bot Script for Ticket Transfer

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

# Function to log into Ticketmaster and retrieve tickets
def get_tickets(email, password):
    login_url = "https://www.ticketmaster.com/login"
    tickets_url = "https://www.ticketmaster.com/my-tickets"

    session = requests.Session()
    payload = {'email': email, 'password': password}
    login_response = session.post(login_url, data=payload)

    if login_response.status_code != 200:
        return None  # Login failed

    response = session.get(tickets_url)
    if response.status_code == 200:
        return response.json()  # This should return a list of tickets
    else:
        return None

# Function to log into Ticketmaster and transfer tickets
def transfer_tickets(email, password, recipient_email):
    login_url = "https://www.ticketmaster.com/login"
    transfer_url = "https://www.ticketmaster.com/transfer"

    session = requests.Session()
    payload = {'email': email, 'password': password}
    login_response = session.post(login_url, data=payload)

    if login_response.status_code != 200:
        return None  # Login failed

    transfer_payload = {'recipient_email': recipient_email}
    response = session.post(transfer_url, data=transfer_payload)

    return response.status_code

# Command to start the bot
def start(update, context):
    update.message.reply_text('Welcome! Please send your email:password and the recipient email.')

# Function to handle messages
def handle_message(update, context):
    try:
        email_password, recipient_email = update.message.text.split(';')
        email, password = email_password.split(':')
        
        # Retrieve tickets before transferring
        tickets = get_tickets(email, password)
        if tickets is None:
            update.message.reply_text('Failed to retrieve tickets. Please check your credentials.')
            return
        
        # Display available tickets
        ticket_list = "\n".join([f"{ticket['name']} - {ticket['date']}" for ticket in tickets])
        update.message.reply_text(f'Available tickets:\n{ticket_list}')
        
        # Proceed with ticket transfer
        status_code = transfer_tickets(email, password, recipient_email)
        
        if status_code == 200:
            update.message.reply_text('Tickets transferred successfully!')
        else:
            update.message.reply_text('Failed to transfer tickets. Please check your credentials.')
    except ValueError:
        update.message.reply_text('Error: Please ensure you are using the correct format: email:password;recipient_email')
    except Exception as e:
        update.message.reply_text('Error: ' + str(e))

# Main function to run the bot
def main():
    # Replace 'YOUR_TOKEN' with your actual Telegram bot token
    updater = Updater('YOUR_TOKEN', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
