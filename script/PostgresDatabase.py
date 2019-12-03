import os
from typing import Dict

from script import PresetInformation
from script.DatabaseInitializer import DatabaseInitializer
from script.DatabaseInterface import DatabaseInterface
from script import TwilioMessaging

import psycopg2

from script.Facades.CreateInvoiceFacade import CreateInvoiceFacade
from script.Facades.InvoiceInfoFacade import InvoiceInfoFacade
from script.Facades.LoginFacade import LoginFacade
from script.Facades.RegisterUserFacade import RegisterUserFacade
from script.Facades.UpdateStatusFacade import UpdateStatusFacade

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
                                                   password="alexyang0204",
                                                   dbname="postgres")
            else:
                self.connection = psycopg2.connect(DATABASE_URL,
                                                   sslmode='require')
            # initialize the db
            self.createInvoice = CreateInvoiceFacade(self.connection)
            self.registerUser = RegisterUserFacade(self.connection)
            self.invoiceInfo = InvoiceInfoFacade(self.connection)
            self.login = LoginFacade(self.connection)
            self.updateStatus = UpdateStatusFacade(self.connection)
            self._initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip" + e.pgerror)

    def create_invoice(self, invoice_info) -> Dict:
        """ Create a new invoice in the database. Return a Dict representing
        the success of the new invoice creation.
        """
        return self.createInvoice.create_invoice(invoice_info)

    def register_user(self, user_info) -> Dict:
        """
         An method to register a new user with user_info in the database
         :param user_info: JSON format argument that contains information
         necessary to create a new user
         :return: A dictionary in the format of {"registerStatus": True/False,
                                                 "errorMessage": "Message"}
         """
        return self.registerUser.register_user(user_info)

    def get_invoice_information(self, username: str):
        """Return the information that would show up on the invoice of a user
        with <username>. """

        return self.invoiceInfo.get_invoice_information(username)

    def attempt_login(self, username: str, password: str) -> Dict:
        """
        An method to attempt a login operation using the username and password
        :param username: username of the login
        :param password: password of the login
        :return: A dictionary in the format of {"loginStatus": True/False,
                                                "userType":"Driver"/"Customer"
                                                /"Supplier"}
        """
        return self.login.attempt_login(username, password)

    def update_status(self, invoice_id: int, status: str):
        """Update the status of the invoice with invoice_id.
        """
        self.updateStatus.update_status(invoice_id, status)

    def _send_message(self, contact, invoice_id, status):
        if status == "onTheWay":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id +\
                      " is on its way!"
            TwilioMessaging.send_message(message, contact['customer'])
        elif status == "arrived":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id +\
                      " delivery has arrived!"
            TwilioMessaging.send_message(message, contact['customer'])
        elif status == "payment":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id +\
                      " has been paid!"
            TwilioMessaging.send_message(message, contact['driver'])

    def _find_contact_by_invoice(self, invoice_id: int):
        cursor = self.connection.cursor()

        cursor.execute("""SELECT customerUsername, driverUsername, supplierUsername
        from Invoices where invoiceID = %s""", (invoice_id,))

        result = cursor.fetchone()

        cursor.execute("""SELECT contact from Customers where username = %s""",
                       (result[0],))
        customer_contact = cursor.fetchone()[0]

        cursor.execute("""SELECT contact from Drivers where username = %s""",
                       (result[1],))
        driver_contact = cursor.fetchone()[0]

        cursor.execute("""SELECT contact from Suppliers where username = %s""",
                       (result[2],))
        supplier_contact = cursor.fetchone()[0]

        return {"customer": customer_contact, "driver": driver_contact,
                "supplier": supplier_contact}

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
            self.create_invoice(PresetInformation.invoice_three)
            self.create_invoice(PresetInformation.invoice_four)
            self.create_invoice(PresetInformation.invoice_five)
            self.create_invoice(PresetInformation.invoice_six)
            self.create_invoice(PresetInformation.invoice_seven)
            self.create_invoice(PresetInformation.invoice_eight)
            self.create_invoice(PresetInformation.invoice_nine)
            self.create_invoice(PresetInformation.invoice_ten)
