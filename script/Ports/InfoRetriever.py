from script.Facades.InfoRetrieverFacade import InfoRetrieverFacade


class InfoRetriever(InfoRetrieverFacade):
    def __init__(self, connection):
        InfoRetrieverFacade.__init__(self, connection)
        self.helpers = _InformationGetters(connection)

    def get_invoice_information(self, username: str):
        """Return the information that would show up on the invoice of a user
        with <username>. """
        cursor = self.connection.cursor()
        cursor.execute("""SELECT userType FROM LoginInfo WHERE username = %s""",
                       (username,))

        user_type = cursor.fetchone()

        if user_type is None:
            return {"infoRequestStatus": False}

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

        return {"infoRequestStatus": True,
                "invoices": self.helpers.generate_invoices(invoices, cursor)}

    def get_user_information(self, username: str):
        cursor = self.connection.cursor()

        cursor.execute("""SELECT userType from loginInfo where username = %s""",
                       (username,))
        result = cursor.fetchone()

        if result is None:
            return {"infoRequestStatus": False}

        user_type = result[0]
        info = self.helpers.get_user_info_as_dict(username, user_type)

        dict = {
            "name": info[0],
            "contact": info[1],
            "address": info[3] if len(info) > 3 else "N/A",
            "bankInformation": info[2] if len(info) > 2 else "N/A",
            "infoRequestStatus": True
        }

        return dict


class _InformationGetters:
    def __init__(self, connection):
        self.connection = connection

    def generate_invoices(self, invoices, cursor) -> list:
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
                temp_orders.append(
                    {
                        "item": order[0],
                        "price": order[1],
                        "amount": order[2]
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
                    "issuedDate": invoice[4],
                    "completionDate": invoice[5],
                    "customerName": customer_info[0],
                    "customerAddress": customer_info[3],
                    "customerContact": customer_info[1],
                    "driverName": driver_info[0],
                    "driverContact": driver_info[1],
                    "driverUsername": driver_info[2],
                    "supplierName": supplier_info[0],
                    "supplierContact": supplier_info[1],
                    "orders": temp_orders,
                    "orderStatus": self._get_status(invoice_id),
                    "infoRequestStatus": True
                }
            )
        return final_invoices

    def get_user_info_as_dict(self, username, user_type):
        info = {}
        if user_type == "Driver":
            info = self._get_driver_info(username)
        elif user_type == "Customer":
            info = self._get_customer_info(username)
        elif user_type == "Supplier":
            info = self._get_supplier_info(username)

        return info

    def _get_customer_info(self, username):
        """Return a tuple of (name, address, contact) of the customer with
        username"""
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name, contact, bankInformation, address 
                            FROM Customers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

    def _get_driver_info(self, username):
        """Return a tuple of (name, contact) of the driver with username"""
        cursor = self.connection.cursor()
        if username is None:
            return "N/A", "N/A", "N/A"

        cursor.execute("""SELECT name, contact, username FROM Drivers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

    def _get_supplier_info(self, username):
        """Return a tuple of (name, contact) of the supplier with username"""
        cursor = self.connection.cursor()
        cursor.execute("""SELECT name, contact, bankInformation FROM Suppliers
                            WHERE username = %s""", (username,))
        return cursor.fetchone()

    def _get_status(self, invoice_id: int):
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
