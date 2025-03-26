class AuthorizationException(Exception):
    def __init__(self, message="Permission denied", status_code=403, *args):
        super().__init__(message, *args)
        self.status_code = status_code

class ActionNotFoundException(Exception):
    def __init__(self, message="Action not found", *args):
        super().__init__(message, *args)