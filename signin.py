from pyrogram import Client, MessageHandler, Message
import os

keys = open("keys.txt","r")
id_ = int(keys.readlines()[0].strip().replace("api_id",""))
hash_ = keys.readlines()[1].strip().replace("api_hash","")
keys.close()

user_app = Client(
    "my_acc",
    api_id=id_,
    api_hash=hash_
)
user_app.start()
user_app.authorize()
user_app.stop()