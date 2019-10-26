from flask import jsonify
class DatabaseInterface:
    """An abstract interface for interaction with a database implementation
    """
    def create_invoice(self, json):
        raise NotImplementedError

    def create_user(self, username: str, user_password: str, user_type: str):
        raise NotImplementedError

    def attempt_login(self, username: str, password: str):
        cursor = self.execute.cursor()
        cursor.exectue("SELECT username, password, user_type FROM login_info WHERE username = %", (username,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"loginAttempt": False})

        elif result[1] == password:
            return jsonify({"loginAttempt": True,
                            "UserType": result[3]})

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

