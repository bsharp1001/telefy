from pyrogram import Client, MessageHandler, Message
import os

keys = open("keys.txt","r")
id_ = int(keys.readline().strip().replace("api_id=",""))
hash_ = keys.readline().strip().replace("api_hash=","")
btoken = keys.readline().strip().replace("bot_token=","")
keys.close()

user_app = Client(
    ":memory:",
    api_id=id_,
    api_hash=hash_
)
bot_app = Client(
    ":memory:",
    api_id=id_,
    api_hash=hash_,
    bot_token=btoken
)

bot_app.start()
bots = open("botsession","w")
bots.write(bot_app.export_session_string())
bots.flush()
bots.close()
bot_app.stop()

user_app.start()
user_app.authorize()
users = open("usersession","w")
users.write(user_app.export_session_string())
users.flush()
users.close()
user_app.stop()