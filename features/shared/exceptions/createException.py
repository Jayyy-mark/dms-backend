class CreateException(Exception):

    def __init__(self, error_message, error=None):
        super.__init__(error_message)
        self.error = error
        