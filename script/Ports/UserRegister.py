from typing import Optional, Dict
from script.Facades.UserRegisterFacade import UserRegisterFacade


class UserRegister(UserRegisterFacade):
    def __init__(self, connection):
        super().__init__(connection)

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
