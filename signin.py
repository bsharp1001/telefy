from pyrogram import Client, MessageHandler, Message
import os
import psycopg2

channel = input("channel :")
id_ = int(input("api id :"))
hash_ = input("api hash :")
btoken = input("bot token :")

DATABASE = os.environ.get('DATABASE_URL')
db = psycopg2.connect(DATABASE)
c = db.cursor()
c.execute('CREATE TABLE users (username text PRIMARY KEY NOT NULL, email text, name text, chatid text)')
db.commit()
c.execute('CREATE TABLE keys (key text PRIMARY KEY NOT NULL, value text)')
db.commit()
c.execute('INSERT INTO keys (key, value) (?,?)',["api_id",id_])
db.commit()
c.execute('INSERT INTO keys (key, value) (?,?)',["api_hash",hash_])
db.commit()
c.execute('INSERT INTO keys (key, value) (?,?)',["bot_token",btoken])
db.commit()
c.execute('INSERT INTO keys (key, value) (?,?)',["channel",channel])
db.commit()

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
c.execute('INSERT INTO keys (key, value) (?,?)',["bot_session",bot_app.export_session_string()])
db.commit()
bot_app.stop()

user_app.start()
user_app.authorize()
c.execute('INSERT INTO keys (key, value) (?,?)',["user_session",user_app.export_session_string()])
db.commit()
db.close()
user_app.stop()