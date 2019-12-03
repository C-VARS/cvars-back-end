from typing import Optional, Dict
from script.Facades.CreateInvoiceFacade import CreateInvoiceFacade


class CreateInvoice(CreateInvoiceFacade):
    def __init__(self, connection):
        CreateInvoiceFacade.__init__(self, connection)

    def create_invoice(self, invoice_info) -> Dict:
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
