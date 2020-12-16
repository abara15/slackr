class AccessError(Exception):
    code = 401
    name = "AccessError"

    def __init__(self, message="Access denied."):
        self.message = message

    def __str__(self):
        return self.message
