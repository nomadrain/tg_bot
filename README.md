# German-English vocabulary teaching Telegram bot
German vocabulary teaching Telegram bot. Reacts with a random word from a limited dictionary (5.8K entries). Supports subscriptions and sends a random word to the subscribed users each 12 hours. Forbids simultanous run of the second copy of the process.

## Requirements
- Python3
- Linux environment
- libraries: pytelegrambotapi

## Install and configure

1. Clone the repository

```
git clone https://github.com/nomadrain/tg_bot.git
```

2. Install the Python dependencies:
```
pip install pytelegrambotapi
```

3. Communicate BotFather bot on Telegram and generate a token for the new bot

4. Change values for the following variables in the beginning of the tg_bot_german.py
```
cd ./tg_bot/
[your editor] ./tg_bot_german.py

logpath = '/path/to/the/log/file/deutsch_bot.log'
dictionarypath = '/path/to/the/json/dictionary/file/deutsch_english.json'
subscriptionsfile = '/path/to/the/subscriptions/file/subscriptions.json'
token = 'the_Telegram_token_generated_for_the_bot_by_BotFather' 

[save]

```

## Run it

Run the application in either way listed below

1. Non-persistent interactive shell (this way is suitable for tests)
```
python ./tg_bot_german.py
```

2. Persistent per-uptime background shell
```
nohup ./tg_bot_german.py &
```

3. Persistent run with hourly restart if application is down
```
crontab -e
(insert the following line at the end of the crontab list, remember to insert the real path)
@hourly nohup /usr/bin/python /pat/to/the/bot/tg_bot_german.py &
```
