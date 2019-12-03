from script.Facades.UpdateStatusFacade import UpdateStatusFacade


class UpdateStatus(UpdateStatusFacade):
    def __init__(self, connection):
        UpdateStatusFacade.__init__(self, connection)

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
        self._send_message(contact, invoice_id, status)

        return {"updateStatus": True}
