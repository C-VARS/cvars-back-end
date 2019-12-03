from twilio.rest import Client
import os

account_sid = os.environ.get("account_sid",
                             'None')
auth_token = os.environ.get("auth_token", 'None')
client = Client(account_sid, auth_token)


def send_message(message_text, target_number):
    message = client.messages \
        .create(
        body=message_text,
        from_='+12564809033',
        to=target_number
    )
    print(message.sid)
