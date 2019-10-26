import os

from DatabaseInitializer import DatabaseInitializer
from DatabaseInterface import DatabaseInterface
import psycopg2

testing = True

DATABASE_URL = os.environ.get("DATABASE_URL", "None")


class PostgresDatabase(DatabaseInterface):

    def __init__(self):
        try:
            if testing:
                self.connection = psycopg2.connect(host="localhost",
                                                   user="postgres",
                                                   password="alexyang0204",
                                                   dbname="postgres")
            else:
                self.connection = psycopg2.connect(DATABASE_URL,
                                                   sslmode='require')
            self.initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip")

    def create_invoice(self, json):
        return "Oopsies"

    def create_user(self, username: str, user_password: str, user_type: str):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT username
                       FROM loginInfo WHERE username = %s""", (username,))
        result = cursor.fetchall()

        if not len(result) == 0:
            return {"signUpStatus": False}
        else:
            valid_type = ["Driver", "Customer", "Supplier"]
            if user_type not in valid_type:
                return {"signUpStatus": False}

            cursor.execute("""INSERT INTO loginInfo VALUES (%s, %s, %s)""", (
                username, user_password, user_type
            ))
            self.connection.commit()
            return {"signUpStatus": True}

    def attempt_login(self, username: str, password: str):
        cursor = self.connection.cursor()
        cursor.execute("""SELECT username, password, usertype 
                       FROM loginInfo WHERE username = %s""",
                       (username,))
        result = cursor.fetchone()

        if result is None or len(result) == 0:
            return {"loginAttempt": False}
        elif result[1] == password:
            return {"loginAttempt": True,
                            "usertype": result[2]}
        else:
            return {"loginAttempt": False}

    def get_order_information(self, username: str):
        return "Oopsies"

    def assign_driver(self, invoice_id: int, username: str):
        return "Oopsies"

    def update_status(self, invoice_id: int, status: str):
        return "Oopsies"

    def confirm_payment(self, invoice_id: int):
        return "Oopsies"

    def initialize(self):
        initializer = DatabaseInitializer(self.connection)
        initializer.initialize()


