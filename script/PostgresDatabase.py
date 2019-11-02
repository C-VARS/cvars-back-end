import datetime
import os
from typing import Optional, Dict

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
                # connect to local db
                self.connection = psycopg2.connect(host="localhost",
                                                   user="postgres",
                                                   password="1234",
                                                   dbname="postgres")
            else:
                self.connection = psycopg2.connect(DATABASE_URL,
                                                   sslmode='require')
            # initialize the db
            self._initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip" + e.pgerror)

    def create_invoice(self, invoice_info):
        """ Return an invoice.
        (Testing method)
        """
        return "Oopsies"

    def register_user(self, user_info) -> Dict:
        """
         An method to register a new user with user_info in the database
         :param user_info: JSON format argument that contains information
         necessary to create a new user
         :return: A dictionary in the format of {"registerStatus": True/False,
                                                 "errorMessage": "Message"}
         """
        error_check_message = self._check_valid_register_input(user_info)
        if error_check_message is not None:
            # there was an error, the user with given user_info is invalid
            return error_check_message

        self.connection.rollback()
        cursor = self.connection.cursor()

        # register a new user
        cursor.execute("""INSERT INTO loginInfo VALUES(%s, %s, %s)""",
                       (user_info['username'], user_info['password'],
                        user_info['userType']))

        # register a new driver
        if user_info['userType'] == 'Driver':
            cursor.execute("""INSERT INTO Drivers VALUES (
            %s, %s, %s)""", (user_info['username'], user_info['name'],
                             user_info['contact']))

        # register a new customer
        elif user_info['userType'] == 'Customer':
            cursor.execute("""INSERT INTO Customers VALUES (
            %s, %s, %s, %s, %s)""", (user_info['username'], user_info['name'],
                                     user_info['bankInformation'],
                                     user_info['address'],
                                     user_info['contact']))
        # register a new supplier
        elif user_info['userType'] == 'Supplier':
            cursor.execute("""INSERT INTO Suppliers VALUES (
            %s, %s, %s, %s)""", (user_info['username'], user_info['name'],
                                 user_info['bankInformation'],
                                 user_info['contact']))
        # update the db
        self.connection.commit()

        return {"registerStatus": True, "errorMessage": ""}

    def _check_valid_register_input(self, user_info) -> Optional[Dict]:
        """
        Check whether the input JSON, user_info, is a valid input for
        user registration.

        Return a dictionary containing the error message if the input is
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

        # Checking if user_info contains all the required information
        if "userType" not in user_info or \
                "username" not in user_info or \
                "password" not in user_info or \
                "name" not in user_info or \
                "contact" not in user_info:
            # Return a dictionary containing the error message
            return {"registerStatus": False,
                    "errorMessage": "Missing information"}

        valid_type = ('Driver', 'Customer', 'Supplier')
        if user_info['userType'] not in valid_type:
            # not valid type error
            return {"registerStatus": False,
                    "errorMessage": "Not a valid user type"}

        if user_info['username'] == "" or user_info['password'] == "":
            # missing information error
            return {"registerStatus": False,
                    "errorMessage": "Missing information"}

        if not user_info['userType'] == "Driver":
            # Customer and Supplier both need bank information for transaction
            if "bankInformation" not in user_info:
                return {"registerStatus": False,
                        "errorMessage": "Missing information"}

        if user_info['userType'] == 'Customer':
            # Customer address is needed for delivery
            if "address" not in user_info:
                return {"registerStatus": False,
                        "errorMessage": "Missing information"}

        username = user_info['username']
        cursor.execute("""SELECT * From loginInfo where username = %s""",
                       (username,))
        result = cursor.fetchall()
        if not len(result) == 0:
            # username must be unique for every user
            return {"registerStatus": False,
                    "errorMessage": "Duplicate username"}

        return None

    def attempt_login(self, username: str, password: str) -> Dict:
        """
        An method to attempt a login operation using the username and password
        :param username: username of the login
        :param password: password of the login
        :return: A dictionary in the format of {"loginStatus": True/False,
                                                "userType":"Driver"/"Customer"
                                                /"Supplier"}
        """
        cursor = self.connection.cursor()
        self.connection.rollback()

        # look for the user with given username
        cursor.execute("""SELECT username, password, userType 
                       FROM loginInfo WHERE username = %s""",
                       (username,))
        result = cursor.fetchone()

        if result is None:
            # user with username does not exist
            return {"loginStatus": False}
        elif result[1] == password:
            # user typed in correct password
            return {"loginStatus": True,
                    "userType": result[2]}
        else:
            # wrong password
            return {"loginStatus": False}

    def get_invoice_information(self, username: str):
        """Return the information that would show up on the invoice of a user
        with <username>. """
        cursor = self.connection.cursor()
        final_invoices = []
        # Assuming it's a customer for now
        # TODO: Add a switch for different customer types
        # TODO: Break this into helpers.
        cursor.execute("""SELECT invoiceID, issuedDate, completionDate 
                        FROM Invoices WHERE customerUsername = %s""",
                       (username,))
        invoices = cursor.fetchall()
        for invoice in invoices:
            temp_orders = []
            invoice_id = invoice[0]
            # Find all orders that are associated with this invoices id
            cursor.execute("""SELECT item, price, amount 
                        FROM Orders WHERE invoiceID = %s""",
                       (invoice_id,))
            orders = cursor.fetchall()
            # We construct a list of orders
            for order in orders:
                temp_orders.append(
                    {
                        "item": order[0],
                        "price": order[1],
                        "amount": order[2]
                    }
                )
            # Construct and append a complete invoice to the list
            final_invoices.append(
                {
                    "invoiceID": invoice[0],
                    "issuedDate": invoice[1],
                    "completionDate": invoice[2],
                    "orders": temp_orders
                }
            )
            return final_invoices

    def assign_driver(self, invoice_id: int, username: str):
        return "Oopsies"

    def get_status(self, invoice_id: int):
        """ Return a JSON file containing the status of the invoice with
        invoice_id

        Precondition: the status columns of the invoice table exists
        """
        cursor = self.connection.cursor()

        # find the invoice with the corresponding invoice_id
        cursor.execute("""SELECT onTheWay, arrived, payment 
                        FROM Invoices WHERE invoiceID = %s""",
                       (invoice_id,))

        # save it as result
        result = cursor.fetchone()

        # return fetched results
        return {"onTheWay": result[0],
                "arrived": result[1],
                "payment": result[2]}

    def confirm_payment(self, invoice_id: int):
        return "Oopsies"

    def _initialize(self) -> None:
        """
        A private method to initialize the database tables using a
        DatabaseInitializer object
        """
        initializer = DatabaseInitializer(self.connection)
        initializer.initialize()
        cursor = self.connection.cursor()

        # Add Seed Data for an example invoice call
        # TODO: Move this somewhere else

        cursor.execute("""INSERT INTO Suppliers VALUES
                ('Sophie', 'Sophie', 'Visa', 'nothing')""")

        cursor.execute("""INSERT INTO Drivers VALUES
                       ('Callum', 'Callum', '123')""")

        cursor.execute("""INSERT INTO Invoices VALUES (%(a)s, %(b)s, %(c)s, %(d)s, %(e)s, %(f)s, %(g)s, %(h)s, %(i)s)
                """, {'a':'87', 'b':'Raag', 'c':'Sophie', 'd':'Callum','e': datetime.date(2005, 11, 18),
                      'f': datetime.date(2007, 11, 18), 'g':True, 'h':False, 'i':False})

        cursor.execute("""INSERT INTO Orders VALUES
                ('Cherry Coke', 72.23, 12, 87)""")

        cursor.execute("""INSERT INTO Orders VALUES
                ('Vanilla Coke', 72.23, 12, 87)""")

