import os
from typing import Dict

from script.DatabaseInitializer import DatabaseInitializer
from script.DatabaseInterface import DatabaseInterface
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL", "None")


class PostgresDatabase(DatabaseInterface):
    """
    An implementation of the DatabaseInterface that handles interaction with a
    PostgresSQL database. Can run either locally or on Heroku
    """

    def __init__(self) -> None:
        """
        Initialize the database interface object by connecting to PostgresSQL
        given the system information of whether it is running local or on
        Heroku
        """
        try:
            if DATABASE_URL == "None":
                self.connection = psycopg2.connect(host="localhost",
                                                   user="postgres",
                                                   password="snamVklY_9683",
                                                   dbname="postgres")
            else:
                self.connection = psycopg2.connect(DATABASE_URL,
                                                   sslmode='require')
            self.initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip" + e.pgerror)

    def create_invoice(self, invoice_info):
        return "Oopsies"

    def register_user(self, user_info) -> Dict:
        """
         An method to register a new user in the database
         :param user_info: JSON format argument that contains information
         necessary to create a new user
         :return: A dictionary in the format of {"registerStatus": True/False,
                                                 "errorMessage": "Message"}
         """
        error_check_message = self._check_valid_register_input(user_info)
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

    def _check_valid_register_input(self, user_info) -> Dict:
        """
        Check whether the input JSON is a valid input for user registration.
        Returns a dictionary containing the error message if the input is
        invalid, otherwise return None
        Error messages:
            - Missing information --> "Missing information"
            - duplicate username --> "Username exists"
            - not valid type --> "Not a valid user type"
            - success --> "Register successful"

        :param user_info: the JSON object containing the register information
        :return: None if the input is correct, a dictionary in the form of
            {"registerStatus": False, "errorMessage": "Message"}
            otherwise
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

        if user_info['username'] == "" or user_info['password'] == "":
            return {"registerStatus": False,
                    "errorMessage": "Missing information"}

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

    def attempt_login(self, username: str, password: str) -> Dict:
        """
        An method to attempt a login operation using the parameters
        :param username: username of the login
        :param password: password of the login
        :return: A dictionary in the format of {"loginStatus": True/False,
                                                "userType":"Driver"/"Customer"
                                                /"Supplier"}
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

    def get_invoice_information(self, username: str):
        return "Oopsies"

    def assign_driver(self, invoice_id: int, username: str):
        return "Oopsies"

    def update_status(self, invoice_id: int, status: str):
        return "Oopsies"

    def confirm_payment(self, invoice_id: int):
        return "Oopsies"

    def initialize(self) -> None:
        """
        A private method to initialize the database tables using a
        DatabaseInitializer object
        """
        initializer = DatabaseInitializer(self.connection)
        initializer.initialize()
