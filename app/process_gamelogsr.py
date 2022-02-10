import telebot
from telebot import types
import requests, json
from config import settings
import schemas



def get_latestgamelogsr(message):


    latest = "Here is your latest gamelog: {0}\n".format(message.from_user.first_name0)
    



