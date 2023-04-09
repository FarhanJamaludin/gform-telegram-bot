import telebot
import json
import requests
from telebot import types

# create a bot instance
TOKEN = '6096237454:AAFdsRH0Vfly-ajPcyq5ptJXd_cJxOTTIx4'
bot = telebot.TeleBot(TOKEN)

# dictionary to store chat IDs
chat_ids = {}

def load_chat_ids():
    try:
        with open("chat_ids.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {'group': None, 'another_group': None}
        
chat_ids = load_chat_ids()

# handle '/start' command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if message.chat.type == 'private' or bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator']:
        bot.reply_to(message, "Hi! Saya adalah BOT untuk Group UPTM Confession. Sila type /help untuk melihat command yang tersedia")
    else:
        bot.reply_to(message, "Maaf, hanya admin yang boleh menggunakan command ini.")


# Command handler for /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if message.chat.type == 'private' or bot.get_chat_member(chat_id, user_id).status in ['creator', 'administrator']:
        help_text = "Command tersedia:\n\n" \
                    "/start - Start the bot\n" \
                    "/help - Show this help message\n\n" \
                    "/getchatID - Get the chat ID for the current chat\n" \
                    "/getchannelID - Get the chat ID for the current channel\n\n" \
                    "/setchatID - Set the chat ID for the main chat\n" \
                    "/setchannelID - Set the channel ID for the channel\n"
        bot.reply_to(message, help_text)
    else:
        bot.reply_to(message, "Maaf, hanya admin yang boleh menggunakan command ini.")

# Command handler for /getchatID command
@bot.message_handler(commands=['getchatID'])
def get_chat_id(message):
    bot.reply_to(message, f"The chat ID is: {message.chat.id}")

# Command handler for /getchannelID command
@bot.channel_post_handler(commands=['getchannelID'])
def reply_with_channel_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"The chat ID for the channel is {chat_id}")


# Command handler for /setchatID command
@bot.message_handler(commands=['setchatID'])
def set_chat_id_command(message):
    user_id = str(message.from_user.id)
    bot.reply_to(message, "Please enter the chat ID for the main group:")
    bot.register_next_step_handler(message, set_main_group_chat_id, user_id)

def set_main_group_chat_id(message, user_id):
    try:
        chat_id = int(message.text)
        user_data = chat_ids.get(user_id, {})
        user_data['group'] = chat_id
        chat_ids[user_id] = user_data
        with open("chat_ids.json", "w") as f:
            json.dump(chat_ids, f)
        bot.reply_to(message, f"Chat ID for the main group has been set to {chat_id}.")
    except ValueError:
        bot.reply_to(message, "Invalid chat ID. Please enter a valid chat ID.")

# Command handler for /setchannelID command
@bot.message_handler(commands=['setchannelID'])
def set_group_chat_id(message):
    user_id = str(message.from_user.id)
    bot.send_message(message.from_user.id, "Please enter the chat ID for the channel:")
    bot.register_next_step_handler(message, set_group_channel_id, user_id)

def set_group_channel_id(message, user_id):
    try:
        channel_id = int(message.text)
        user_data = chat_ids.get(user_id, {})
        user_data['another_group'] = channel_id
        chat_ids[user_id] = user_data
        with open("chat_ids.json", "w") as f:
            json.dump(chat_ids, f)
        bot.reply_to(message, f"Channel ID for your group has been set to {channel_id}.")
    except ValueError:
        bot.reply_to(message, "Invalid channel ID. Please enter a valid channel ID.")


# callback function to handle button click
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    
    if call.data == 'btn1':
        # get user ID
        user_id = str(call.from_user.id)

        # check if another_group is set for the user
        if 'another_group' in chat_ids.get(user_id, {}):

            # send the message to another group
            chat_id = chat_ids[user_id]['another_group']
            text = call.message.text 
            bot.send_message(chat_id, text)
            bot.answer_callback_query(call.id, 'Message sent to the other group')

            # update the button to show it has been approved
            message_id = call.message.message_id
            chat_id = call.message.chat.id
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('✅ Approved', callback_data='approved'))
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "The 'another_group' chat ID has not been set yet. Please use the /setchannelID command to set it up.")

    elif call.data == 'btn2':

        # update the button to show it has been rejected
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('❌ Rejected', callback_data='rejected'))
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


bot.polling()
