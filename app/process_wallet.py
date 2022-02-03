import telebot
from telebot import types
import requests, json
from config import settings
import schemas


def get_walletsbyperson(message):
    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/walletsbyperson/{message.chat.id}"
    response = requests.get(url)

    data = json.loads(response.text)

    i = 1
    txtwallet = ""

    if response.status_code == 200:
        for wallets in data:
            txtwallet += "Wallet {0}\n".format(i)
            for k, v in wallets.items():
                ##rvalue += "Alias: \n".format(wallet['alias'])
                txtwallet += "{0}: {1}\n".format(k, v)
            txtwallet += "\n"
            i += 1

        return txtwallet
    else:
        return "no wallets found."


def get_walletcount(message):
    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/walletsbyperson/{message.chat.id}"
    response = requests.get(url)

    wallets = json.loads(response.text)

    if response.status_code == 200:
        return len(wallets)
    else:
        return 0

def post_wallet(chatid: int, alias: str, walletaddress: str):
    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/wallets"

    body = {'walletaddress': walletaddress, 'alias': alias,'walletownerid': chatid}

    response = requests.post(url, json=body)

    if response.status_code == 201:
        return "created"
    else:
        return "failed"


