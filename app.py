# SETUP: LOAD bot_local.py
from bot_local import *

# SETUP: FLASK (WEB FRAMEWORK)
from flask import Flask, request
app = Flask(__name__)

# SERVER SIDE: main route
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
   json_string = request.stream.read().decode("utf-8")
   update = telebot.types.Update.de_json(json_string)
   bot.process_new_updates([update])
   return "Bot is running", 200

# SERVER SIDE: webhook
@app.route("/")
def webhook():
   bot.remove_webhook()
   # TO DO: Edit the value of variable heroku_app_name according to your Heroku application name
   heroku_app_name = "dacp-phoenix-maulana-telebot"

   # NOTE: You need to use a publically available URL that the Telegram servers can reach.
   bot.set_webhook(url=f'https://{heroku_app_name}.herokuapp.com/{TOKEN}')
   return "Bot is running", 200

if __name__ == "__main__":
    app.run()