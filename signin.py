from pyrogram import Client, MessageHandler, Message
import os

user_app = Client(
    "my_acc",
    api_id=os.environ.get("api_id"),
    api_hash=os.environ.get("api_hash")
)
user_app.start()
user_app.authorize()
user_app.stop()