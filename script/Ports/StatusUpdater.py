from script.Facades.StatusUpdaterFacade import StatusUpdaterFacade

from script import TwilioMessaging
from script.FirebaseSender import FirebaseSender


class StatusUpdater(StatusUpdaterFacade):
    def __init__(self, connection):
        super().__init__(connection)
        self.fb = FirebaseSender()

    def update_status(self, invoice_id: int, status: str):
        """Update the status of the invoice with invoice_id.
        """
        cursor = self.connection.cursor()

        if status == "onTheWay":
            cursor.execute("""UPDATE Invoices SET onTheWay = NOT onTheWay
                            WHERE invoiceID = %s""", (invoice_id,))
        elif status == "arrived":
            cursor.execute("""UPDATE Invoices SET arrived = NOT arrived
                            WHERE invoiceID = %s""", (invoice_id,))
        elif status == "payment":
            cursor.execute("""UPDATE Invoices SET payment = NOT payment, 
                            completionDate = current_timestamp
                            WHERE invoiceID = %s""", (invoice_id,))
        else:
            return {"updateStatus": False}

        self.connection.commit()

        contact = self._find_contact_by_invoice(invoice_id)

        msg = "Invoice No." + invoice_id + " status has been updated"
        self.fb.send_message_to_topic(msg, invoice_id)

        try:
            self._send_text_message(contact, invoice_id, status)
        except Exception as e:
            print("Twilio messaging error!")

        return {"updateStatus": True}

    def _send_text_message(self, contact, invoice_id, status):
        if status == "onTheWay":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id + \
                      " is on its way!"
            TwilioMessaging.send_message(message, contact['customer'])
        elif status == "arrived":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id + \
                      " delivery has arrived!"
            TwilioMessaging.send_message(message, contact['customer'])
        elif status == "payment":
            message = "ScotiaTracker Reminder: Invoice #" + invoice_id + \
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
