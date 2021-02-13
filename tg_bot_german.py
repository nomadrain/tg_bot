#!/usr/bin/env python3

# pip install pytelegrambotapi
import traceback
import threading
import telebot
import json
import random
import sys
import os
import time
import socket
import requests
import logging
from typing import List

resend_message_interval = 60 * 60 * 12
logpath = 'deutsch_bot.log'
dictionarypath = 'deutsch_english.json'
subscriptionsfile = 'subscriptions.json'
token = 'sometoken'

session = requests.Session()
session.verify = True

last_user_id = None
bot = None
subscriptions: List[int] = []

dictionary: str = str
with open(dictionarypath) as dct:
    dictionary = json.load(dct)


def log_factory(logfile, filemode='a'):
    logging.basicConfig( 
        filename=logfile, 
        filemode=filemode, 
        format='%(asctime)s : %(levelname)s : %(message)s', 
        level='INFO' )

    return logging.getLogger("Logger")

lg = log_factory(logpath)

if os.path.exists(subscriptionsfile):
    try:
        with open(subscriptionsfile) as sfile:
            subscriptions = json.load(sfile)
    except Exception as err:
        lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during loading the subscriptions')

def dump_subscr():
    try:
        with open(subscriptionsfile, 'w') as sfile:
            json.dump(subscriptions, sfile, indent=4, ensure_ascii=False)
    except Exception as err:
        lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during dumping the subscriptions')


def subscribe(user_id: int):
    """
    :type user_id: int
    """
    try:
        if user_id not in subscriptions:
            subscriptions.append(user_id)
            dump_subscr()
            bot.send_message(user_id, 'You have been subscribed for the updates')
            lg.info(f'User {user_id} has been subscribed for the updates')
            lg.info(f'Current subscriptions are: {str(subscriptions)}')
        else:
            bot.send_message(user_id, 'You are already subscribed :-)')
    except Exception as err:
        lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during adding a subscription')


def unsubscribe(user_id: int):
    try:
        if user_id in subscriptions:
            subscriptions.remove(user_id)
            dump_subscr()
            bot.send_message(user_id, 'You have been unsubscribed from the updates')
            lg.info(f'User {user_id} has been unsubscribed from the updates')
            lg.info(f'Current subscriptions are: {str(subscriptions)}')
        else:
            bot.send_message(user_id, 'you are not subscribed, please use /subscribe first')
    except Exception as err:
        lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during removing a subscription')


def send_wort(user_id: int):
    if bot:
        wort = random.choice(list(dictionary.keys()))
        translation = dictionary[wort]
        bot.send_message(user_id, f'<b>{wort}</b>\n<pre>\t\t\t\t{translation}</pre>', parse_mode='HTML')


class BackgroundTimer(threading.Thread):
    
    def run(self):
        while True:
            time.sleep(resend_message_interval)
            try:
                for next_user_id in subscriptions:
                    send_wort(next_user_id)
            except Exception as err:
                lg.error(traceback.format_exc())
                lg.error(str(err) + ' - this error caught during auto resend')


try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind('\0deutsch_bot_lock')
    lg.info(f'Deutsch bot started. Resend interval is {resend_message_interval}')
    lg.info(f'Current subscriptions are: {str(subscriptions)}')
except socket.error as e:
    lg.info("The instance of the bot is already running. Another instance won't start")
    sys.exit(0)

bot = telebot.TeleBot(token)

timer = BackgroundTimer()
timer.start()


@bot.message_handler(commands=['start', 'help', 'subscribe', 'unsubscribe'])
def send_welcome(message):
    try:
        global last_user_id
        last_user_id = message.from_user.id
        if '/subscribe' in message.text:
            subscribe(last_user_id)
        elif '/unsubscribe' in message.text:
            unsubscribe(last_user_id)
        else:
            bot.reply_to(message,
                         f'''I am a German words teaching bot. Glad to see you,
{message.from_user.first_name} {message.from_user.last_name}!

Type "wort" to see a random Deutsch word from the mini-dictionary.

You can subscribe for updates from the bot by typing /subscribe command. Then it will send you a new random word each 12 hours. To cancel your existing subscription please use /unsubscribe command.

Please enjoy! :-)
''')
            lg.info(f'{message.from_user.first_name} {message.from_user.last_name} connected')
    except Exception as err:
        # lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during greeting')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global last_user_id
    last_user_id = message.from_user.id
    try:
        if 'hello' in message.text.lower():
            bot.send_message(message.from_user.id, f'Hello, {message.from_user.first_name}')
        elif 'wort' in message.text.lower():
            send_wort(last_user_id)
        else:
            bot.send_message(message.from_user.id, 'Sorry, I cannot understand')
    except Exception as err:
        lg.error(traceback.format_exc())
        lg.error(str(err) + ' - this error caught during regular message processing')
        lg.info('Retrying to send message in 5 seconds')
        time.sleep(5)
        get_text_messages(message)


try:
    bot.polling(none_stop=True)
except Exception as err:
    lg.error(traceback.format_exc())
    lg.error(str(err) + ' - this error caught during bot.polling')
    sys.exit(2)
