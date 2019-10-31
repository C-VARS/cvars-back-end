from typing import Dict


class DatabaseInterface:
    """An abstract interface for interaction with a database implementation
    """

    def create_invoice(self, invoice_info) -> Dict:
        """
        An abstract method to create an invoice in the database
        :param invoice_info: JSON format argument that contains information
        necessary to create an invoice
        :return: A dictionary in the format of {"creationSuccess": True/False}
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
        raise NotImplementedError

    def assign_driver(self, invoice_id: int, username: str):
        raise NotImplementedError

    def update_status(self, invoice_id: int, status: str):
        raise NotImplementedError

    def confirm_payment(self, invoice_id: int):
        raise NotImplementedError

    def initialize(self) -> None:
        """
        An abstract private method to initialize the
        """
        raise NotImplementedError

