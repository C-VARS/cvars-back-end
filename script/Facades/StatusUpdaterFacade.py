class StatusUpdaterFacade:
    def __init__(self, connection):
        self.connection = connection

    def update_status(self, invoice_id: int, status: str):
        """Update the status of the invoice with invoice_id.
        """
        raise NotImplementedError
