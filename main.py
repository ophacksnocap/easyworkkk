import telebot
import os
import requests
from bs4 import BeautifulSoup

API_TOKEN = '7297098002:AAGaCltHCKy-9PCZEiBDeyKW7nm4lw0oT6U'  # Replace with your actual API token
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to the Subway Order Bot! Please enter your email and password in the format: email:password")

@bot.message_handler(func=lambda message: ':' in message.text)
def login(message):
    email, password = message.text.split(':')
    session = requests.Session()
    login_url = 'https://www.subway.com/en-us/auth/signin?url=/en-us'
    response = session.post(login_url, json={'email': email, 'password': password})
    
    if response.status_code == 200:
        bot.send_message(message.chat.id, "Login successful! Retrieving your saved cards...")
        get_user_cards(message, session)
    else:
        bot.send_message(message.chat.id, "Login failed. Please check your credentials.")

def get_user_cards(message, session):
    cards_url = 'https://www.subway.com/en-us/profile/paymentmethods'  # Updated URL
    response = session.get(cards_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = []  # List to hold card information
        
        # Assuming the cards are in a specific HTML structure
        for card in soup.find_all('div', class_='card-info'):  # Adjust class name as necessary
            card_type = card.find('span', class_='card-type').text  # Adjust selector as necessary
            last4 = card.find('span', class_='last4').text  # Adjust selector as necessary
            cards.append({'type': card_type, 'last4': last4})
        
        if cards:
            card_list = "\n".join([f"{card['type']} ending in {card['last4']}" for card in cards])
            bot.send_message(message.chat.id, f"Your saved cards:\n{card_list}\nPlease enter your food order.")
            bot.register_next_step_handler(message, order_food, session)
        else:
            bot.send_message(message.chat.id, "No saved cards found.")
    else:
        bot.send_message(message.chat.id, "Could not retrieve your cards.")

def order_food(message, session):
    food_order = message.text
    bot.send_message(message.chat.id, "Please enter your delivery address.")
    bot.register_next_step_handler(message, delivery_address, session, food_order)

def delivery_address(message, session, food_order):
    address = message.text
    bot.send_message(message.chat.id, f"You ordered: {food_order}\nDelivery address: {address}\nDo you want to proceed with the order? (yes/no)")
    bot.register_next_step_handler(message, confirm_order, session, food_order, address)

def confirm_order(message, session, food_order, address):
    if message.text.lower() == 'yes':
        card_type = 'Visa'  # Example card type
        card_number = '0000' if card_type in ['Visa', 'MasterCard'] else '0000'
        
        order_url = 'https://subway.com/api/order'
        order_data = {
            'food_order': food_order,
            'delivery_address': address,
            'card_number': card_number
        }
        
        response = session.post(order_url, json=order_data)
        
        if response.status_code == 200:
            bot.send_message(message.chat.id, "Your order has been placed successfully!")
        else:
            bot.send_message(message.chat.id, "There was an error placing your order.")
    else:
        bot.send_message(message.chat.id, "Order canceled.")

bot.polling()
