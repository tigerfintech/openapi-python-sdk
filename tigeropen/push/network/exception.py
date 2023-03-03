
class PushException(Exception):
    pass


class ConnectionClosedException(PushException):
    pass


class NotConnectedException(PushException):
    """
    Raised when there is currently no server connection.
    """


class ConnectFailedException(PushException):
    """
    Raised by Connection.attempt_connection when reconnection attempts
    have exceeded Connection.__reconnect_attempts_max.
    """


class InterruptedException(PushException):
    """
    Raised by receive when data read is interrupted.
    """
