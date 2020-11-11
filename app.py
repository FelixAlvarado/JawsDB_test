from flask import Flask, request, render_template, send_from_directory
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os
import threading
import random
import string

load_dotenv()

user = os.environ.get("AWS_USERNAME")
password = os.environ.get("AWS_PASSWORD")
DB_NAME = os.environ.get("AWS_DB_NAME")
port = os.environ.get("AWS_PORT")
host = os.environ.get("AWS_HOST")



cnx = mysql.connector.connect(user=f"{user}", password=f"{password}",database=f"{DB_NAME}", host=f"{host}", port=f"{port}")
cursor = cnx.cursor(buffered=True)
cursor.execute("USE {}".format(DB_NAME))

#class used to reinitialize the mysql connection every 290 seconds. mysql times out inactive connections
class Database:
    def __init__(self, cursor_value, cnx_value):
        self.cursor = cursor_value
        self.cnx = cnx_value

    def restart_connection(self):
        self.cnx = mysql.connector.connect(user=f"{user}", password=f"{password}",database=f"{DB_NAME}", host=f"{host}", port=f"{port}")
        self.cursor = self.cnx.cursor(buffered=True)
        self.cursor.execute("USE {}".format(DB_NAME))

database = Database(cursor, cnx)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


set_interval(database.restart_connection,290)


app = Flask(__name__, static_folder='frontend/build')

# set_interval(restart_connection(mysql,cursor, cnx, user,password, DB_NAME, host, port),28700)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


set_interval(database.restart_connection,290)


app = Flask(__name__)

@app.route('/test_create', methods=["GET"])
def test_create():
    letters = string.ascii_lowercase
    created_string = ''.join(random.choice(letters) for i in range(20))

    test_format = ("INSERT INTO test "
        "(name) "
        "VALUES (%s)")

    test_data = (created_string,)

    database.cursor.execute(test_format, test_data)

    database.cnx.commit()

    id = database.cursor.lastrowid

    return f"Entry successfully created. the id of the new entry is {id}. New Entry is {created_string}"

@app.route('/test_retrieve', methods=["GET"])
def test_retrieve():

    result_string = ''

    database.cursor.execute("SELECT * FROM test")
    result_string += 'Here are all entries for the table:  '

    for entry in cursor:
        print('here is the entry')
        print(entry)
        result_string += f"id: {entry[0]} name: {entry[1]}                "
    
    return result_string

if __name__ == "__main__":
    app.run(debug=True)

