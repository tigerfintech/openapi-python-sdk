
class PushException(Exception):
    """
    Common exception class. All specific stomp.py exceptions are subclasses
    of StompException, allowing the library user to catch all current and
    future library exceptions.
    """


class ConnectionClosedException(PushException):
    """
    Raised in the receiver thread when the connection has been closed
    by the server.
    """


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
