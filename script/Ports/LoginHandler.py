from jinja2.nodes import Dict

from script.Facades.LoginHandlerFacade import LoginHandlerFacade


class LoginHandler(LoginHandlerFacade):
    def __init__(self, connection):
        super().__init__(connection)
        self.connection = connection

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
