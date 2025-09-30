class UserAlreadyExists(Exception):
    pass


class InvalidOTP(Exception):
    pass


class ExpiredOTP(Exception):
    pass


class MailerError(Exception):
    """Raised when mail delivery fails."""

    pass
