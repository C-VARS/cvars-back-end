from twilio.rest import Client
import os

account_sid = os.environ.get("account_sid",
                             'None')
auth_token = os.environ.get("auth_token", 'None')
client = Client(account_sid, auth_token)


def send_message(messageText, targetNumber):
    return 1
