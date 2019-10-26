from flask import Flask, request
import DatabaseInterface as db

app = Flask(__name__)

# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "Just testing"

# login
@app.route("/users/login")
def login():
    """
    Login this user
    :return: json
    """
    username = request.args.get('username')
    password = request.args.get('password')

    return db.attempt_login(username, password)





