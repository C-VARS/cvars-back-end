import os

from DatabaseInitializer import DatabaseInitializer
from DatabaseInterface import DatabaseInterface
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "None")


class PostgresDatabase(DatabaseInterface):

    def __init__(self):
        try:
            if DATABASE_URL == "None":
                self.connection = psycopg2.connect(host="localhost",
                                                   user="postgres",
                                                   password="alexyang0204",
                                                   dbname="postgres")
            else:
                self.connection = psycopg2.connect(DATABASE_URL,
                                                   sslmode='require')
            self.initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip" + e.pgerror)

    def create_invoice(self, json):
        return "Oopsies"

    def register_user(self, user_info):
        """Create a user with <username>, <user_password>, <user_type>.
        Return JSON with different signUpStatus:
            - duplicate username --> "Username exists"
            - not valid type --> "Not a valid user type"
            - signed up --> "Signup successful"
        """
        return "blopp"

    def attempt_login(self, username: str, password: str):
        """Return a JSON indicating if a login attempt was successful with
        given <username> and <password>.
        """
        cursor = self.connection.cursor()
        cursor.execute("""SELECT username, password, usertype 
                       FROM loginInfo WHERE username = %s""",
                       (username,))
        result = cursor.fetchone()

        if result is None:
            return {"loginStatus": False}
        elif result[1] == password:
            return {"loginStatus": True,
                            "usertype": result[2]}
        else:
            return {"loginStatus": False}

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

        cursor = self.connection.cursor()

        cursor.execute("SELECT * From loginInfo")

        if len(cursor.fetchall()) == 0:

            cursor.execute("""INSERT INTO loginInfo VALUES 
            ('Callum', 'callum12345', 'Driver')""")

            cursor.execute("""INSERT INTO loginInfo VALUES 
            ('Vlad', 'vlad12345', 'Customer')""")

            cursor.execute("""INSERT INTO loginInfo VALUES 
            ('Alex', 'alex12345', 'Driver')""")

            cursor.execute("""INSERT INTO loginInfo VALUES 
            ('Raag', 'raag12345', 'Customer')""")

            cursor.execute("""INSERT INTO loginInfo VALUES 
            ('Sophie', 'sophie12345', 'Supplier')""")

            self.connection.commit()



