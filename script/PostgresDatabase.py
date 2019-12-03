import os
from typing import Dict

from script import PresetInformation
from script.DatabaseInitializer import DatabaseInitializer
from script.DatabaseInterface import DatabaseInterface

import psycopg2

from script.Ports.InvoiceCreator import InvoiceCreator
from script.Ports.InfoRetriever import InfoRetriever
from script.Ports.LoginHandler import LoginHandler
from script.Ports.UserRegister import UserRegister
from script.Ports.StatusUpdater import StatusUpdater

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
            self.invoice_creator = InvoiceCreator(self.connection)
            self.user_register = UserRegister(self.connection)
            self.info_retriever = InfoRetriever(self.connection)
            self.login_handler = LoginHandler(self.connection)
            self.status_updater = StatusUpdater(self.connection)
            self._initialize()
        except psycopg2.OperationalError as e:
            print("Something happened rip" + e.pgerror)

    def create_invoice(self, invoice_info) -> Dict:
        """ Create a new invoice in the database. Return a Dict representing
        the success of the new invoice creation.
        """
        return self.invoice_creator.create_invoice(invoice_info)

    def register_user(self, user_info) -> Dict:
        """
         An method to register a new user with user_info in the database
         :param user_info: JSON format argument that contains information
         necessary to create a new user
         :return: A dictionary in the format of {"registerStatus": True/False,
                                                 "errorMessage": "Message"}
         """
        return self.user_register.register_user(user_info)

    def get_user_information(self, username: str):
        """
        Return a dictionary of a given user's information
        :param username: the user's username
        :return: Dictionary object containing the user's relevant information
        """
        return self.info_retriever.get_user_information(username)

    def get_invoice_information(self, username: str):
        """Return the information that would show up on the invoice of a user
        with <username>. """

        return self.info_retriever.get_invoice_information(username)

    def attempt_login(self, username: str, password: str) -> Dict:
        """
        An method to attempt a login operation using the username and password
        :param username: username of the login
        :param password: password of the login
        :return: A dictionary in the format of {"loginStatus": True/False,
                                                "userType":"Driver"/"Customer"
                                                /"Supplier"}
        """
        return self.login_handler.attempt_login(username, password)

    def update_status(self, invoice_id: int, status: str):
        """Update the status of the invoice with invoice_id.
        """
        return self.status_updater.update_status(invoice_id, status)

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
