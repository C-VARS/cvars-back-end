from typing import Optional, Dict


class InvoiceCreatorFacade:
    def __init__(self, connection):
        self.connection = connection

    def create_invoice(self, invoice_info) -> Dict:
        """ Create a new invoice in the database. Return a Dict representing
        the success of the new invoice creation.
        """
        pass

