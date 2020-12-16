from werkzeug.exceptions import HTTPException


class ValueError(HTTPException):
    code = 400
    name = "ValueError"

    def __str__(self):
        return self.description
