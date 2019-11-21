import firebase_admin
from firebase_admin import credentials, messaging


class FirebaseSender:

    def __init__(self):
        cred = credentials.Certificate("./script/firebaseAuthKey.json")
        self.app = firebase_admin.initialize_app(cred)

    def send_message_to_topic(self, message, topic):

        firebase_message = messaging.Message(
            data={
                'message': message
            },
            topic=topic,
        )

        response = messaging.send(firebase_message)
        print("successfully sent ", response)
