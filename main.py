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
    login_url = 'https://id.subway.com/02d64b66-5494-461d-8e0d-5c72dc1efa7f/oauth2/v2.0/authorize?p=b2c_1a_signup_signin-r2&ui_locales=en-US&sessionid=07207926a3bd46848ef651f87b3234d9&client_id=502546f5-a6d5-48ed-be47-6c7a5c984770&redirect_uri=https%3A%2F%2Fwww.subway.com%2F&response_type=code%20id_token&scope=openid&state=OpenIdConnect.AuthenticationProperties%3Ddqu634nOzhDUZBNZJmMKT6bMJu8ooxuRkPrHs7bgztnvQoeODFMl5MvuP4TdibupaaVtlXdtMKX56M7R_j8tsrCWKvwX5OzOY8A5my2JBP_5oDSQ37Gy8UMbvnYvkWaF1aX_q0b1teTR7PWy92x9DeOF_S3dQXjFrN8w4d_ndVXWQNeGuibmqfQSe8zH0mbCYSaI1YYixEHdrMVuUkUguLEzTsH8LYwWShVr8NPUsHdCVl5s2IaZ1Ft_HcpLLVYHB_wostTEipz3eqeVNwTZUTCoo3B7PFUrnt1YxOo20SNac25pLWJbTbwDlGxEoGqiOJQ5s_9bzfH8x7AlAZ1nYMo8FNVge2_5eyoA2rJMc4d51_JCCKvYnLnscgmvCuMHKgnI95Sj_OPSiQ9TM3ssCZFOdAHj31b-Zu989oIpE4Id_2i_BC27lO_ajQ9db_8g2dbAWGHpKIyNUR_y4amKS9uDmDE&response_mode=form_post&nonce=638659225052233090.NTVmYWFhMGItZjAwOS00NzJmLWIyZGYtMjQ2OTcxZjEzZTgxZDVmZTc0YzQtNTljYy00YTZiLWExODktNGQ3NDRlNDc4ZjEz&x-client-SKU=ID_NET461&x-client-ver=5.3.0.0'
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
