from pyrogram import Client, MessageHandler, Message
import sqlite3
from flask import Flask, render_template, request, g, redirect, url_for
import os
from os import path
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email, EqualTo

DATABASE = 'users.db'
app = Flask(__name__)

channelf = open("channel.txt","r")
channel = channelf.readline().strip()
channelf.close()
keys = open("keys.txt","r")
id_ = int(keys.readline().strip().replace("api_id=",""))
hash_ = keys.readline().strip().replace("api_hash=","")
keys.close()

user_app = Client(
    "my_acc",
    api_id=id_,
    api_hash=hash_
)
user_app.start()

bot_app = Client(
    "my_bot",
    api_id=id_,
    api_hash=hash_,
    bot_token="1195224941:AAGAypEBx3qyw1RMaaAzR-gNbQhexQa1XD4"
)
bot_app.start()


if path.exists(DATABASE) == False:
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute('CREATE TABLE users (username text PRIMARY KEY NOT NULL, email text, name text, chatid text)')
    db.commit()

class UserChannelEmailNameForm(Form):
    user = StringField('Username', validators=[DataRequired()], _name="user")
    channel = StringField('Channel', validators=[DataRequired()], _name="channel")
    email = StringField('Email', validators=[], _name="email")
    name = StringField('Name', validators=[], _name="name")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchone() if one else cur.fetchall() 
    cur.close()
    return rv

users = query_db("SELECT * FROM users")

def on_confirm_messeage_recieve(client, mes):
    with app.app_context():
        cmd = "INSERT INTO users(username, chatid) VALUES(?,?) ON CONFLICT(username) DO UPDATE SET chatid=?"
        username = mes.chat.username
        chatid = mes.chat.id
        res = query_db(cmd, [username, chatid, chatid], True)
        query_db("SELECT * FROM users")
        bot_app.send_message("861406121","hello there, welcome to telefy. I'll be your personal Notification bot, if the channel you specified made any new announcement, I'll notify you in no time. cheers "+u'\U0001F601')

handlr = MessageHandler(on_confirm_messeage_recieve)
bot_app.add_handler(handlr)

def register_user(username, name = None, email = None):
    cmd = "SELECT * FROM users WHERE username = ?"
    res = query_db(cmd, [username], True)
    users = query_db("SELECT * FROM users")
    if res is not None and res[0] == username and res['chatid'] is not None:
        cmd = "UPDATE users SET (name = ?, email = ?) WHERE username = ?"
        res = query_db(cmd, [name, email, username])
        return redirect(url_for('dashboard',q=0))
    else:
        cmd = "INSERT INTO users (username, name, email) (?,?,?)"
        res = query_db(cmd, [username, name, email])
        return redirect(url_for('dashboard',q=1))

def login_user(username, name = None, email = None):
    cmd = "SELECT * FROM users WHERE username = ?"
    res = query_db(cmd, [username], True)
    if res is not None and res[0] == username and res['chatid'] is not None:
        return redirect(url_for('dashboard',q=0))
    else:
        return redirect(url_for('dashboard',q=1))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def enter():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserChannelEmailNameForm()
    if form.validate_on_submit():
        username = form.user
        name = form.name
        email = form.email
        register_user(username, name, email)

    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserChannelEmailNameForm()
    if form.validate_on_submit():
        username = form.user
        login_user(username)

    return render_template("login.html", form=form)

@app.route('/dashboard/<q>')
def dashboard(q):
    if q == 1:
        return render_template("dashboard.html", mes="Great! Everything done. Whenever new announcements are pulished on the channel specified, our bot will notify you.")

    return render_template("dashboard.html", mes="You signed up successfully but seems like you still didn't message our bot. Unfortunately, a bot can't open a chat on its own according to telegram rules. When you have a moment, be sure to send @ChannelGrabber_bot a message. To confirm your sent message, please login")

def getNew():
    update = user_app.get_history(channel,limit=1)
    file_ = open("msg_id.txt", "r+")
    lst_id = file_.readline().strip()
    if lst_id != update.message_id:
        file_.write(str(update.message_id))
        file_.close()
        for user in users:
            bot_app.forward_messages(user["chatid"],channel,update.message_id)
    
announcement_handlr = MessageHandler(getNew)
user_app.add_handler(announcement_handlr)