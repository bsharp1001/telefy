from pyrogram import Client, MessageHandler, Message
import psycopg2
from flask import Flask, render_template, request, g, redirect, url_for, abort
import os
from os import path
import urllib.request as req
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Email, EqualTo
import threading
import time
import re

def stayawake():
    while True:
        time.sleep(60)
        if os.environ.get("app_url",None) is not None:
            req.urlopen(os.environ.get("app_url"))

keepup = threading.Thread(target=stayawake,daemon=True)
keepup.start()

DATABASE = os.environ.get('DATABASE_URL')

app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    )

class UserChannelEmailNameForm(Form):
    user = StringField('Username*:', validators=[DataRequired()], _name="user")
    email = StringField('Email:', validators=[], _name="email")
    name = StringField('Full Name:', validators=[], _name="name")

class UserForm(Form):
    user = StringField('Username', validators=[DataRequired()], _name="user")
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
    if cur.description is not None:
        rv = cur.fetchone() if one else cur.fetchall() 
        cur.close()
        return rv
    return None

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

def opt_in(username, chatid):
    
    cmd = "INSERT INTO users (username, chatid, email, name) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO UPDATE SET chatid=%s"
    res = query_db(cmd, [username, chatid, "", "", chatid], True)
    bot_app.send_message(int(chatid),"Great, a new friend. Always nice to have new friend, welcome. If you care to tell me more info about you type \n /add_info")

def opt_out(username):
    cmd = "DELETE FROM users WHERE username=%s"
    query_db(cmd, [username], True)

def add_info(mes, chatid, username):
    mes = str(mes).replace("info:","").replace("info","")
    name = email = ""
    if mes.find("email:") != -1 and mes.find("name:") != -1:
        name = re.sub(r'email:\S+\s*','',mes).split("name:")[1].strip()
        email = re.sub(r'name:\S+\s*','',mes).split("email:")[1].strip()
    elif mes.find("email:") == -1 and mes.find("name:") != -1:
        name = mes.split("name:")[1].strip()
    elif mes.find("email:") != -1 and mes.find("name:") == -1:
        email = mes.split("name:")[1].strip()

    if re.match(r'[A-Z-z]{1,}', name) is not None and re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email) is not None:
        cmd = "UPDATE users SET name=%s, email=%s WHERE username = %s"
        res = query_db(cmd, [name, email, username])
        bot_app.send_message(int(chatid),"Nice! everything is added")

    elif re.match(r'[A-Z-z]{1,}', name) is None and re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email) is not None:
        cmd = "UPDATE users SET email=%s WHERE username = %s"
        res = query_db(cmd, [email, username])
        bot_app.send_message(int(chatid),"Seems like something is wrong with the name form. To add it right follow the following form:\n\n info: \n name:Joe Smith")

    elif re.match(r'[A-Z-z]{1,}', name) is not None and re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email) is None:
        cmd = "UPDATE users SET name=%s WHERE username = %s"
        res = query_db(cmd, [name, username])
        bot_app.send_message(int(chatid),"Seems like something is wrong with the name form. To add it right follow the following form:\n\n info: \n email:email@example.com")

def check_info(username, chatid):
    users = query_db("SELECT * FROM users WHERE username = %s", [username], True)
    email = users[1]
    name = users[2]

    if email == "" and name == "":
        bot_app.send_message(int(chatid),"Perfect! it is always nice to know my friends better. You can add an email and/or a name. To add info follow the following form:\n\n info: \n email:email@example.com \n name:Joe Smith")

    elif email == "" and name != "":
        bot_app.send_message(int(chatid),"Seems like You added a name but not an email. To add info follow the following form:\n\n info: \n name:Joe Smith")

    elif email != "" and name == "":
        bot_app.send_message(int(chatid),"Seems like You added an email but not a name. To add info follow the following form:\n\n info: \n email:email@example.com")

def on_confirm_messeage_recieve(client, mes):
    with app.app_context():
        username = mes.chat.username
        if username is None:
            username = "no username"
        print(username)
        chatid = mes.chat.id
        if mes.text == "/start":
            opt_in(username, chatid)
        elif mes.text == "/add_info":
            check_info(username, chatid)
        elif mes.text == "/opt_out":
            bot_app.send_message(int(chatid),"Goodbyes hve always been hard "+u'\U0001F97A'+". As you wish, you will stop receiving notifications from me")
            time.sleep(5)
            opt_out(username, chatid)
        elif mes.text.find("info:"):
            add_info(mes.text, chatid, username)

handlr = MessageHandler(on_confirm_messeage_recieve)
bot_app.add_handler(handlr)

def getNew(client, mes):
    with app.app_context():
        users = query_db("SELECT * FROM users")
        if mes.chat.username == channel:
            for user in users:
                if user[3] is not None:
                    bot_app.forward_messages(int(user[3]),channel,mes.message_id, as_copy=True)
    
announcement_handlr = MessageHandler(getNew)
user_app.add_handler(announcement_handlr)

'''def register_user(username, name = "", email = ""):
    cmd = "SELECT * FROM users WHERE username = %s"
    res = query_db(cmd, [username], True)
    users = query_db("SELECT * FROM users")
    if res is not None and res[0] == username and res[3] is not None:
        cmd = "UPDATE users SET name=%s, email=%s WHERE username = %s"
        res = query_db(cmd, [name, email, username])
        return 0
    else:
        cmd = "INSERT INTO users (username, name, email) VALUES (%s,%s,%s)"
        res = query_db(cmd, [username, name, email])
        return 1

def login_user(username, name = None, email = None):
    cmd = "SELECT * FROM users WHERE username = %s"
    res = query_db(cmd, [username], True)
    if res is not None and res[0] == username and res[3] is not None:
        return 0
    else:
        return 1'''

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def enter():
    abort(410)
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    abort(410)
    form = UserChannelEmailNameForm()
    if form.validate_on_submit():
        username = form.user.data.replace("@","")
        name = form.name.data
        email = form.email.data
        return redirect(url_for('dashboard',q=str(register_user(username, name, email))))

    return render_template("register.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    abort(410)
    form = UserForm()
    if form.validate_on_submit():
        username = form.user.data
        return redirect(url_for('dashboard',q=str(login_user(username))))

    return render_template("login.html", form=form)

@app.route('/dashboard/<q>')
def dashboard(q):
    abort(410)
    if q == "0":
        return render_template("dashboard.html", mes="Great! Everything done. Whenever new announcements are pulished on the channel specified, our bot will notify you.")
    else:
        return render_template("dashboard.html", mes="You signed up successfully but seems like you still didn't message our bot. Unfortunately, a bot can't open a chat on its own according to telegram rules. When you have a moment, be sure to send @ChannelGrabber_bot a message. To confirm your sent message, please login")
