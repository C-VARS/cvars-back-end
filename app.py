from flask import Flask, request, jsonify
import DatabaseInterface, PostgresDatabase

app = Flask(__name__)
db = PostgresDatabase.PostgresDatabase()

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

    return jsonify(db.attempt_login(username, password))

if __name__ == '__main__':
    app.run()





