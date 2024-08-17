from fastapi import HTTPException, status
from fastapi import HTTPException, status

class HTTPExceptions(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

    @staticmethod
    def not_found(detail: str = "Resource not found"):
        return HTTPExceptions(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    @staticmethod
    def bad_request(detail: str = "Bad request"):
        return HTTPExceptions(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @staticmethod
    def unauthorized(detail: str = "Unauthorized"):
        return HTTPExceptions(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

    @staticmethod
    def forbidden(detail: str = "Forbidden"):
        return HTTPExceptions(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @staticmethod
    def internal_server_error(detail: str = "Internal server error"):
        return HTTPExceptions(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)