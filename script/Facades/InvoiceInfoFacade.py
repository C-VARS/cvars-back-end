class InvoiceInfoFacade:
    def __init__(self, connection):
        self.connection = connection

    def get_invoice_information(self, username: str):
        """Return the information that would show up on the invoice of a user
        with <username>. """
        pass
