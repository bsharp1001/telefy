from pyrogram import Client, MessageHandler
import sqlite3
conn = sqlite3.connect('example.db')

def func(client, mes):
    print(mes)

app2 = Client(
    "my_acc",
    api_id=1685407,
    api_hash="f81ba833ff82e70b4d04c1b3ab655ebf",
)

app2.start()
j = app2.get_history("pythony",10)
print(j)

file = open("msg_id.txt", "r+")
print(file.readline().strip())
file.close()

'''handlr = MessageHandler(func)

app2.add_handler(handlr)
app2.send_message("861406121","hello there, will send you notifs on this cht from telefy")'''