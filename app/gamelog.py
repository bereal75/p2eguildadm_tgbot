import telebot
import requests, json
from config import settings
import schemas



def get_latest(message):

    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/gamelogsr/latest/{message.chat.id}"
    response = requests.get(url)

    gamelog = json.loads(response.text)

    return gamelog