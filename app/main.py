import telebot
from telebot import types
import logging
import sys
from pydantic import BaseModel
from typing import Optional
import requests
import json
import process_person, process_wallet
import gamelog
from config import settings

api_key = settings.tg_api_key
bot = telebot.TeleBot(api_key)

bot_user = {}
# wallet_dict = {0: {'walletownerid': 0, 'alias': 'n/a', 'walletaddress': 'n/a'}}
wallet_dict = {}

# TODO implementing logging
logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%m-%d %H:%M:%S')
ch = logging.StreamHandler(sys.stdout)
fh = logging.FileHandler('p2eguildadm_tgbot.log')                                                                                                                                                                                
ch.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)
logger.setLevel(logging.INFO)  # or use logging.INFO


# setting up keyboards
wallet_markup = telebot.types.InlineKeyboardMarkup()
markup = telebot.types.ReplyKeyboardMarkup()
markup = telebot.types.ReplyKeyboardRemove(selective=False)

### message handlers ###

# help aka start

@bot.message_handler(commands=['start', 'help'])
def start(message):
  with open('chat_commands.txt', 'r') as file:
    data = file.read()
  bot.reply_to(message, data, parse_mode="MarkdownV2")

# konichiwa
@bot.message_handler(commands=['konichiwa'])
def mh_konichiwa(message):
    bot.reply_to(message, 'Konichiwa, Shogun!')


# whoami
@bot.message_handler(commands=['whoami'])
def whoami(message):
    
    # reply with the whoami message
    bot.reply_to(message, process_person.get_whoami(message))


# signup
@bot.message_handler(commands=['signup'])
def signup(message):
    wallet_markup = telebot.types.InlineKeyboardMarkup()
    if process_person.check_userregistered(message) == False:
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='signup!', callback_data=3))
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='cancel', callback_data=99)) 
        bot.reply_to(message, text="You have not signed up yet.\n Click on button signup below or cancel.", reply_markup=wallet_markup)
    else:
        wallet_markup = telebot.types.InlineKeyboardMarkup()
        bot.reply_to(message, f"You have already signed up to this guild!!\n So let's rather say: Welcome back, {message.from_user.first_name}.\nHave a look at /wallet now.\n")
         

# latest gamelog
@bot.message_handler(commands=['latest'])
def latest(message):
    bot.reply_to(message, gamelog.get_latest())




# quit
@bot.message_handler(commands=['quit'])
def quit(message):
    wallet_markup = telebot.types.InlineKeyboardMarkup()
    wallet_markup.add(telebot.types.InlineKeyboardButton(text='quit!', callback_data=90))
    wallet_markup.add(telebot.types.InlineKeyboardButton(text='cancel', callback_data=99))

    bot.reply_to(message, text="Do you really want to quit? ##ALL## your data (wallets, decks, performance) will be deleted from the guild database.", reply_markup=wallet_markup)

# wallet
@bot.message_handler(commands=['wallet'])
def setup_wallet(message):
    wallet_markup = telebot.types.InlineKeyboardMarkup()   
    if process_person.check_userregistered(message) == True:

        wallet_count = process_wallet.get_walletcount(message)

        if wallet_count > 0:
            wallet_markup.add(telebot.types.InlineKeyboardButton(text='list wallet(s)', callback_data=1))
            wallet_markup.add(telebot.types.InlineKeyboardButton(text='remove wallet', callback_data=4))

        wallet_markup.add(telebot.types.InlineKeyboardButton(text='register wallet', callback_data=2))
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='cancel', callback_data=99))

        bot.reply_to(message, text="Wallet maintenance", reply_markup=wallet_markup)
       
    else:
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='signup', callback_data=3))
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='cancel', callback_data=99))
        bot.reply_to(message, text="You have not signed up yet.\n Click on button signup below or cancel.", reply_markup=wallet_markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    cid = call.message.chat.id
    cmsg = call.message.reply_to_message
    bot.answer_callback_query(callback_query_id=call.id)

    # list wallets
    if call.data == '1':
        wallets = process_wallet.get_walletsbyperson(cmsg)
        bot.send_message(call.message.chat.id,"list of wallet(s):")
        bot.send_message(call.message.chat.id,wallets)

    # register wallet
    elif call.data == '2':
        wallet_markup = telebot.types.InlineKeyboardMarkup()
        wallet_markup.add(telebot.types.InlineKeyboardButton(text='cancel', callback_data=99))
        wallet_dict[cid] = {}
        wallet_dict[cid]["walletownerid"]=cid
        print(wallet_dict)
        print("current cid:")
        print(wallet_dict[cid])
        sent = bot.send_message(call.message.chat.id, "Enter alias", reply_markup=wallet_markup)
        bot.register_next_step_handler(sent,get_alias)

    # signup
    elif call.data == '3':

        signup_result = process_person.create_user(cmsg) 
        print("signup_result: {0}".format(signup_result))

        if signup_result == "created":
            bot.send_message(cid, 'You signed the contract with blood {0}.\nWe are glad you are with us for the ride.\nHave a look at /wallet now.\n'.format(cmsg.from_user.first_name))
        if signup_result == "failed":
            bot.send_message(cid, 'Signing up did not work. Please come again later and try it again. Press on /signup')
        if signup_result == "existing":
            bot.send_message(cid, f"You have already signed up to this endeavour!!\n So let's rather say: Welcome back, {cmsg.from_user.first_name}.\nHave a look at /wallet now.\n")


    elif call.data == '4':
        bot.send_message(call.message.chat.id,"remove wallet. ##TODO ##")
    
    elif call.data == '90':
        quit_result = process_person.delete_user(cmsg)
        print("quit_result: {0}".format(quit_result))

        if quit_result == "deleted":
            bot.send_message(cid, 'You have left us. What a pity!')
        if quit_result == "failed":
            bot.send_message(cid, 'Quitting the guild did not work. Please try again or contact the administrator.')

    elif call.data == '99':
        bot.send_message(call.message.chat.id,"cancelled")

    bot.edit_message_reply_markup(call.message.chat.id, call.message.id)
         


def get_alias(message):
    alias = message.text
    wallet_dict[message.chat.id]["alias"]=alias
    sent = bot.send_message(message.chat.id,"Enter walletaddress.")
    bot.register_next_step_handler(sent,get_walletaddress)


def get_walletaddress(message):
    walletaddress = message.text
    wallet_dict[message.chat.id]["walletaddress"]=walletaddress
    print(wallet_dict)
    bot.send_message(message.chat.id,"storing data...")
    wallet_register_result = process_wallet.post_wallet(wallet_dict[message.chat.id]["walletownerid"], wallet_dict[message.chat.id]["alias"], wallet_dict[message.chat.id]["walletaddress"])
    print(wallet_register_result)
    if wallet_register_result == "created":
        bot.send_message(wallet_dict[message.chat.id]["walletownerid"], 'Wallet has been registered.')
    elif wallet_register_result == "failed":
        bot.send_message(wallet_dict[message.chat.id]["walletownerid"], 'Registering wallet failed.')
    
    wallet_markup = telebot.types.InlineKeyboardMarkup()


bot.infinity_polling(interval=5)

