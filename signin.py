from pyrogram import Client, MessageHandler, Message

user_app = Client("my_acc")
user_app.start()
user_app.authorize()