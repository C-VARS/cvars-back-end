from twilio.rest import Client
import os

account_sid = os.environ.get("account_sid",
                             'AC4164a655996eb4aafa3ba61d40120731')
auth_token = os.environ.get("auth_token", '1b7955c78b1356c84cf188b8f4a3c758')
client = Client(account_sid, auth_token)


def send_message(messageText, targetNumber):
    message = client.messages \
        .create(
        body=messageText,
        from_='+12564809033',
        to=targetNumber
    )
    print(message.sid)
