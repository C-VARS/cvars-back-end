class DatabaseInterface:
    """An abstract interface for interaction with a database implementation
    """

    def create_invoice(self, invoice_info):
        raise NotImplementedError

    def register_user(self, user_info):
        raise NotImplementedError

    def attempt_login(self, username: str, user_password: str):
        raise NotImplementedError

    def get_order_information(self, username: str):
        raise NotImplementedError

    def assign_driver(self, invoice_id: int, username: str):
        raise NotImplementedError

    def update_status(self, invoice_id: int, status: str):
        raise NotImplementedError

    def confirm_payment(self, invoice_id: int):
        raise NotImplementedError

    def initialize(self):
        raise NotImplementedError

