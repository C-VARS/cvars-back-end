from flask import Flask

app = Flask(__name__)

# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "Just testing"