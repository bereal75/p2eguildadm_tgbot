from http.client import HTTPResponse
import telebot
import requests, json
from config import settings
import schemas


def get_whoami(message):
  #logger.INFO("whoami triggered for <{0}>".format(message.from_user))
  
  whoami = f"Your Telegram Chat Id: {message.chat.id}\n"
  whoami += f"Your Telegram User Id: {message.from_user.id}\n"
  whoami += f"Your User Name: {message.from_user.username}\n"
  whoami += f"Your First Name: {message.from_user.first_name}\n"
  whoami += f"Your Last Name: {message.from_user.last_name}\n"
  whoami += f"Chat type: {message.chat.type}\n\n"

  # check if user is registered already. If not display signup link
  if check_userregistered(message) == False:
    whoami += "You have not signed up yet.\n Enter /signup to signup for the guild.\n"
  else:
    whoami += "You have signed up already, that\'s good!\nEnter /wallet to register or maintain wallet(s).\n"
  
  return whoami

# signup
def create_user(message):
  response = ""

  if check_userregistered(message) == False and check_isbot(message) == False :
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/persons"


    body = {'personid': message.from_user.id, 'firstname' : message.from_user.first_name, 'lastname' : message.from_user.last_name, 'tgusername': message.from_user.username}

    response = requests.post(url, json=body)

    if response.status_code == 201:
      return "created"
    else:
      return "failed"

  else:
    return "existing"

# quit
def delete_user(message):
  response = ""
  if check_userregistered(message) == True and check_isbot(message) == False :
    url = "http://{0}:{1}/persons/{2}".format(settings.p2eguildadm_api_host, settings.p2eguildadm_api_port, message.chat.id)
    response = requests.delete(url)
  if response.status_code == 204:
    return "deleted"
  else:
    return "failed"
    



# Check if user himself is a bot too
def check_isbot(message):
  if message.from_user.is_bot == True:
    return True
  else:
    return False

# check if a user has already signed up for the guild
def check_userregistered(message):
    response = ""
    url = f"http://{settings.p2eguildadm_api_host}:{settings.p2eguildadm_api_port}/persons/{message.chat.id}"
    response = requests.get(url)

    if response.status_code == 404:
      return False
    else:

      return True