from flask import Flask, request, jsonify, abort
import PostgresDatabase

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


@app.route("/users/login", methods=['GET'])
def login():
    """
    Login this user
    :return: json
    """
    username = request.args.get('username', "")
    password = request.args.get('password', "")

    return jsonify(db.attempt_login(username, password))


@app.route("/users/register", methods=["POST"])
def register_user():
    register_info = request.get_json()
    if not register_info:
        abort(400)
    return jsonify(db.register_user(register_info))


if __name__ == '__main__':
    app.run()
