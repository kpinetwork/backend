class AppError(Exception):
    """General exception"""

    pass


class AuthError(AppError):
    """Authentication exception"""

    pass


class QueryError(AppError):
    """Query exception"""

    pass
