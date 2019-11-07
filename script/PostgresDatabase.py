import os
from typing import Optional, Dict

from script import PresetInformation
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

    def create_invoice(self, invoice_info) -> Dict:
        """ Create a new invoice in the database. Return a Dict representing
        the success of the new invoice creation.
        """
        valid_status = self._check_valid_invoice_input(invoice_info)
        if valid_status is not None:
            return valid_status

        self.connection.rollback()
        cursor = self.connection.cursor()

        if "driverUsername" in invoice_info:
            cursor.execute("""INSERT INTO Invoices (customerUsername, 
            supplierUsername, driverUsername) VALUES (%s, %s, %s) RETURNING 
            invoiceID""", (
                invoice_info["customerUsername"],
                invoice_info["supplierUsername"],
                invoice_info["driverUsername"]
            ))
        else:
            cursor.execute("""INSERT INTO Invoices (customerUsername, 
                                supplierUsername) VALUES (%s, %s) RETURNING
                                invoiceID """, (
                invoice_info["customerUsername"],
                invoice_info["supplierUsername"]
            ))

        invoice_id = cursor.fetchone()[0]
        self._insert_orders_for_invoice(invoice_id, invoice_info["orders"])

        self.connection.commit()

        return {"invoiceCreationStatus": True, "errorMessage": ""}

    def _insert_orders_for_invoice(self, invoice_id, orders) -> None:
        cursor = self.connection.cursor()
        for order in orders:
            cursor.execute("""INSERT INTO Orders VALUES(%s, %s, %s, %s) """,
                           (order["item"], order["price"], order["amount"],
                            invoice_id))

    def _check_valid_invoice_input(self, invoice_info) -> Optional[Dict]:
        """
        Check whether the input JSON, invoice_info, is a valid input for
        the creation of a new invoice
        :param invoice_info: the JSON information for the new invoice
        :return: None if the input is correct, a dictionary containing the
        error message and invoice creation status if incorrect
        """
        self.connection.rollback()
        cursor = self.connection.cursor()

        if "customerUsername" not in invoice_info or \
                "supplierUsername" not in invoice_info or \
                "orders" not in invoice_info:
            return {"invoiceCreationStatus": False,
                    "errorMessage": "Missing information"}

        customer_username = invoice_info["customerUsername"]
        cursor.execute("SELECT userType From loginInfo where username = %s",
                       (customer_username,))
        result = cursor.fetchone()
        if result is None or not result[0] == "Customer":
            return {"invoiceCreationStatus": False,
                    "errorMessage": "False customer information"}

        supplier_username = invoice_info["supplierUsername"]
        cursor.execute("SELECT userType From loginInfo where username = %s",
                       (supplier_username,))
        result = cursor.fetchone()
        if result is None or not result[0] == "Supplier":
            return {"invoiceCreationStatus": False,
                    "errorMessage": "False supplier information"}

        if "driverUsername" in invoice_info:
            driver_username = invoice_info["driverUsername"]
            cursor.execute("SELECT userType From loginInfo where username = %s",
                           (driver_username,))
            result = cursor.fetchone()
            if result is None or not result[0] == "Driver":
                return {"invoiceCreationStatus": False,
                        "errorMessage": "False driver information"}

        orders = invoice_info["orders"]
        if isinstance(orders, list) and len(orders) > 0:
            for element in orders:
                if "item" not in element or "price" not in element or "amount" \
                        not in element:
                    return {"invoiceCreationStatus": False,
                            "errorMessage": "Incorrect order information"}
        else:
            return {"invoiceCreationStatus": False,
                    "errorMessage": "Incorrect order information"}

        return None

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
        cursor.execute("""SELECT userType FROM LoginInfo WHERE username = %s""",
                       (username,))

        user_type = cursor.fetchone()

        if user_type is None:
            return {"invoiceFetchStatus": False}

        elif user_type[0] == "Driver":
            cursor.execute("""SELECT * FROM Invoices 
                            WHERE driverUsername = %s""", (username,))

        elif user_type[0] == "Supplier":
            cursor.execute("""SELECT * FROM Invoices 
                            WHERE supplierUsername = %s""", (username,))

        elif user_type[0] == "Customer":
            cursor.execute("""SELECT * FROM Invoices 
                            WHERE customerUsername = %s""", (username,))
        invoices = cursor.fetchall()

        return self._generate_invoices(invoices, cursor)

    def _generate_invoices(self, invoices, cursor) -> list:
        final_invoices = []
        for invoice in invoices:
            temp_orders = []
            total = 0
            invoice_id = invoice[0]
            # Find all orders that are associated with this invoices id
            cursor.execute("""SELECT item, price, amount 
                        FROM Orders WHERE invoiceID = %s""",
                           (invoice_id,))
            orders = cursor.fetchall()
            # We construct a list of orders, calculate total price
            for order in orders:
                price = order.get("price")
                amount = order.get("amount")
                total += price * amount
                temp_orders.append(
                    {
                        "item": order[0],
                        "price": price,
                        "amount": amount
                    }
                )
            # Construct and append a complete invoice to the list

            # get actual names, addresses, contacts of users
            customer_info = self._get_customer_info(invoice[1])
            supplier_info = self._get_supplier_info(invoice[2])
            driver_info = self._get_driver_info(invoice[3])

            final_invoices.append(
                {
                    "invoiceID": invoice[0],
                    "issuedDate": invoice[1],
                    "completionDate": invoice[2],
                    "CustomerName": customer_info[0],
                    "CustomerAddress": customer_info[1],
                    "CustomerContact": customer_info[2],
                    "DriverName": driver_info[0],
                    "DriverContact": driver_info[1],
                    "SupplierName": supplier_info[0],
                    "SupplierContact": supplier_info[1],
                    "orders": temp_orders,
                    "Total": total,
                    "orderStatus": self.get_status(invoice_id),
                }
            )
        return final_invoices

    def _get_customer_info(self, username):
        """Return a tuple of (name, address, contact) of the customer with
        username"""
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name, address, contact FROM Customers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

    def _get_driver_info(self, username):
        """Return a tuple of (name, contact) of the driver with username"""
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name, contact FROM Drivers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

    def _get_supplier_info(self, username):
        """Return a tuple of (name, contact) of the supplier with username"""
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name, contact FROM Suppliers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

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

        if result is None:
            return {"onTheWay": False,
                    "arrived": False,
                    "payment": False}

        # return fetched results
        return {"onTheWay": result[0],
                "arrived": result[1],
                "payment": result[2]}

    def confirm_payment(self, invoice_id: int):
        return "Oopsies"

    def update_status(self, invoice_id: int, status: dict):
        """Update the status of the invoice with invoice_id.

        Precondition: Only one state of the status is True, and the state that
        is True should be the only state that is updated.
        """
        cursor = self.connection.cursor()

        for state in status:
            if status[state]:
                to_update = state

        cursor.execute(f"""UPDATE Invoices SET {to_update} = NOT {to_update}
                        WHERE invoiceID = {invoice_id}""")

        self.connection.commit()

    def _initialize(self) -> None:
        """
        A private method to initialize the database tables using a
        DatabaseInitializer object
        """
        initializer = DatabaseInitializer(self.connection)
        initializer.initialize()

        cursor = self.connection.cursor()
        cursor.execute("SELECT * from loginInfo")

        if cursor.fetchone() is None:
            self.register_user(PresetInformation.Alex)
            self.register_user(PresetInformation.Callum)
            self.register_user(PresetInformation.Raag)
            self.register_user(PresetInformation.Sophie)
            self.register_user(PresetInformation.Vlad)
            self.create_invoice(PresetInformation.invoice_one)
            self.create_invoice(PresetInformation.invoice_two)
