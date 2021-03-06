from typing import Dict


class DatabaseInterface:
    """An abstract interface for interaction with a database implementation
    """

    def create_invoice(self, invoice_info) -> Dict:
        """
        An abstract method to create an invoice in the database
        :param invoice_info: JSON format argument that contains information
        necessary to create an invoice
        :return: A dictionary in the format of
        {"invoiceCreationStatus": True/False}
        """
        raise NotImplementedError

    def register_user(self, user_info) -> Dict:
        """
        An abstract method to register a new user in the database
        :param user_info: JSON format argument that contains information
        necessary to create a new user
        :return: A dictionary in the format of {"registerStatus": True/False}
        """
        raise NotImplementedError

    def attempt_login(self, username: str, password: str) -> Dict:
        """
        An abstract method to attempt a login operation using the parameters
        :param username: username of the login
        :param password: password of the login
        :return: A dictionary in the format of {"loginStatus": True/False,
                                                "userType":"Driver"/"Customer"
                                                /"Supplier"}
        """
        raise NotImplementedError

    def get_invoice_information(self, username: str):
        """
        An abstract method to get invoice information related to the user
        :param username: username of the user
        :return: a list of dictionaries containing all the invoices relevant
        to the user
        """
        raise NotImplementedError

    def get_user_information(self, username: str):
        """
        An abstract method to get all the information related to a user
        :param username: username of the user
        :return: A dictionary of the user information
        """
        raise NotImplementedError

    def update_status(self, invoice_id: int, status: str):
        """Update the status of the invoice with invoice_id.
        """
        raise NotImplementedError
