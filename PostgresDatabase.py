import os

from DatabaseInitializer import DatabaseInitializer
from DatabaseInterface import DatabaseInterface
import psycopg2
import json

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

    def create_invoice(self, invoice_info):
        return "Oopsies"

    def check_valid_invoice_input(self, invoice_info):
        return "blop"

    def register_user(self, user_info):
        """Create a user with the given field contained in the JSON parameter
        Return the error message defined in check_valid_register_input if the
        JSON information is invalid.
        """
        error_check_message = self.check_valid_register_input(user_info)
        if error_check_message is not None:
            return error_check_message

        self.connection.rollback()
        cursor = self.connection.cursor()

        cursor.execute("""INSERT INTO loginInfo VALUES(%s, %s, %s)""",
                       (user_info['username'], user_info['password'],
                        user_info['userType']))
        if user_info['userType'] == 'Driver':
            cursor.execute("""INSERT INTO Drivers VALUES (
            %s, %s, %s)""", (user_info['username'], user_info['name'],
                             user_info['contact']))
        elif user_info['userType'] == 'Customer':
            cursor.execute("""INSERT INTO Customers VALUES (
            %s, %s, %s, %s, %s)""", (user_info['username'], user_info['name'],
                                     user_info['bankInformation'],
                                     user_info['address'],
                                     user_info['contact']))
        elif user_info['userType'] == 'Supplier':
            cursor.execute("""INSERT INTO Suppliers VALUES (
            %s, %s, %s, %s)""", (user_info['username'], user_info['name'],
                                 user_info['bankInformation'],
                                 user_info['contact']))
        self.connection.commit()

        return {"registerStatus": True, "errorMessage": ""}

    def check_valid_register_input(self, user_info):
        """Check whether the input JSON is a valid input for user registration.
        Returns a dictionary containing the error message if the input is
        invalid, otherwise return None
        Error messages:
            - Missing information --> "Missing information"
            - duplicate username --> "Username exists"
            - not valid type --> "Not a valid user type"
            - success --> "Register successful"
        """

        self.connection.rollback()
        cursor = self.connection.cursor()

        if "userType" not in user_info or \
                "username" not in user_info or \
                "password" not in user_info or \
                "name" not in user_info or \
                "contact" not in user_info:
            return {"registerStatus": False,
                    "errorMessage": "Missing information"}

        valid_type = ('Driver', 'Customer', 'Supplier')
        if user_info['userType'] not in valid_type:
            return {"registerStatus": False,
                    "errorMessage": "Not a valid user type"}

        if not user_info['userType'] == "Driver":
            if "bankInformation" not in user_info:
                return {"registerStatus": False,
                        "errorMessage": "Missing information"}

        if user_info['userType'] == 'Customer':
            if "address" not in user_info:
                return {"registerStatus": False,
                        "errorMessage": "Missing information"}

        username = user_info['username']
        cursor.execute("""SELECT * From loginInfo where username = %s""",
                       (username,))
        result = cursor.fetchall()
        if not len(result) == 0:
            return {"registerStatus": False,
                    "errorMessage": "Duplicate username"}

        return None

    def attempt_login(self, username: str, password: str):
        """Return a JSON indicating if a login attempt was successful with
        given <username> and <password>. If it is, the JSON field
        "usertype" will contain the string that represent the type of user
        that associates with this username.
        """
        cursor = self.connection.cursor()
        self.connection.rollback()
        cursor.execute("""SELECT username, password, userType 
                       FROM loginInfo WHERE username = %s""",
                       (username,))
        result = cursor.fetchone()

        if result is None:
            return {"loginStatus": False}
        elif result[1] == password:
            return {"loginStatus": True,
                    "userType": result[2]}
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
