from pyrogram import Client, MessageHandler, Message
import psycopg2
from flask import Flask, render_template, request, g, redirect, url_for
import os
from os import path
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email, EqualTo

DATABASE = os.environ.get('DATABASE_URL')

app = Flask(__name__)
'''if path.exists(DATABASE) == False:
    db = psycopg2.connect(DATABASE)
    c = db.cursor()
    c.execute('CREATE TABLE users (username text PRIMARY KEY NOT NULL, email text, name text, chatid text)')
    db.commit()'''

class UserChannelEmailNameForm(Form):
    user = StringField('Username', validators=[DataRequired()], _name="user")
    channelw = StringField('Channel', validators=[DataRequired()], _name="channel")
    email = StringField('Email', validators=[], _name="email")
    name = StringField('Name', validators=[], _name="name")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    rv = cur.fetchone() if one else cur.fetchall() 
    cur.close()
    return rv

def startpy():
    with app.app_context():
        _channel = query_db("SELECT * FROM keys WHERE key = %s", ["channel"],True)[1]
        _id_ = int(query_db("SELECT * FROM keys WHERE key = %s", ["api_id"],True)[1])
        _hash_ = query_db("SELECT * FROM keys WHERE key = %s", ["api_hash"],True)[1]
        _btoken = query_db("SELECT * FROM keys WHERE key = %s", ["bot_token"],True)[1]
        _botstring = query_db("SELECT * FROM keys WHERE key = %s", ["bot_session"],True)[1]
        _userstring = query_db("SELECT * FROM keys WHERE key = %s", ["user_session"],True)[1]
        
        return ["none", _channel,_id_,_hash_,_btoken,_botstring,_userstring]


data = startpy()
channel = data[1]
id_ = data[2]
hash_ = data[3]
btoken = data[4]
botstring = data[5]
userstring = data[6]

user_app = Client(
    userstring,
    api_id=id_,
    api_hash=hash_
)
user_app.start()
bot_app = Client(
    botstring,
    api_id=id_,
    api_hash=hash_,
    bot_token=btoken
)
bot_app.start()

def on_confirm_messeage_recieve(client, mes):
    with app.app_context():
        cmd = "INSERT INTO users(username, chatid) VALUES (%s,%s) ON CONFLICT(username) DO UPDATE SET chatid=%s"
        username = mes.chat.username
        chatid = mes.chat.id
        res = query_db(cmd, [username, chatid, chatid], True)
        bot_app.send_message("861406121","hello there, welcome to telefy. I'll be your personal Notification bot, if the channel you specified made any new announcement, I'll notify you in no time. cheers "+u'\U0001F601')

handlr = MessageHandler(on_confirm_messeage_recieve)
bot_app.add_handler(handlr)

def getNew(client, mes):
    with app.app_context():
        users = query_db("SELECT * FROM users")
        if mes.chat.username == channel:
            for user in users:
                bot_app.forward_messages(user[3],channel,mes.message_id, as_copy=True)
    
announcement_handlr = MessageHandler(getNew)
user_app.add_handler(announcement_handlr)

def register_user(username, name = None, email = None):
    cmd = "SELECT * FROM users WHERE username = %s"
    res = query_db(cmd, [username], True)
    users = query_db("SELECT * FROM users")
    if res is not None and res[0] == username and res['chatid'] is not None:
        cmd = "UPDATE users SET (name = %s, email = %s) WHERE username = %s"
        res = query_db(cmd, [name, email, username])
        return redirect(url_for('dashboard',q=0))
    else:
        cmd = "INSERT INTO users VALUES (username, name, email) (%s,%s,%s)"
        res = query_db(cmd, [username, name, email])
        return redirect(url_for('dashboard',q=1))

def login_user(username, name = None, email = None):
    cmd = "SELECT * FROM users WHERE username = %s"
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
