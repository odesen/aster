from fastapi import HTTPException, status


class AsterException(Exception):
    """Base exception class for Aster"""

    detail: str
    """Exception details"""


class ClientException(HTTPException):
    """Client error"""

    status_code: int = status.HTTP_400_BAD_REQUEST


class NotAuthorizedException(ClientException):
    status_code: int = status.HTTP_401_UNAUTHORIZED


class PermissionDeniedException(ClientException):
    status_code: int = status.HTTP_403_FORBIDDEN


class NotFoundException(ClientException):
    status_code: int = status.HTTP_404_NOT_FOUND


class InternalServerException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
