"""General utility functions.
"""

import socket
import threading

from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon

CMD_TYPE_NAME_MAP = {
    SocketCommon.Command.CONNECT: 'connecting',
    SocketCommon.Command.CONNECTED: 'connected',
    SocketCommon.Command.DISCONNECT: 'disconnecting',
    SocketCommon.Command.ERROR: 'error',
    SocketCommon.Command.HEARTBEAT: 'heartbeat',
    SocketCommon.Command.MESSAGE: 'message',
    SocketCommon.Command.SEND: 'send',
    SocketCommon.Command.SUBSCRIBE: 'subscribe',
    SocketCommon.Command.UNKNOWN: 'unknown',
    SocketCommon.Command.UNSUBSCRIBE: 'unsubscribe',
}


def get_command_name(cmd_type):
    return CMD_TYPE_NAME_MAP.get(cmd_type, 'unknown')


LOCALHOST_NAMES = ["localhost", "127.0.0.1"]


try:
    LOCALHOST_NAMES.append(socket.gethostbyname(socket.gethostname()))
except Exception:
    pass

try:
    LOCALHOST_NAMES.append(socket.gethostname())
except Exception:
    pass

try:
    LOCALHOST_NAMES.append(socket.getfqdn(socket.gethostname()))
except Exception:
    pass


def is_eol_default(c):
    return c == b"\x0a"


def default_create_thread(callback):
    """
    Default thread creation - used to create threads when the client doesn't want to provide their
    own thread creation.

    :param function callback: the callback function provided to threading.Thread
    """
    thread = threading.Thread(None, callback)
    thread.daemon = True  # Don't let thread prevent termination
    thread.start()
    return thread


def is_localhost(host_and_port):
    """
    Return 1 if the specified host+port is a member of the 'localhost' list of hosts, 2 if not (predominately used
    as a sort key.

    :param (str,int) host_and_port: tuple containing host and port

    :rtype: int
    """
    (host, _) = host_and_port
    if host in LOCALHOST_NAMES:
        return 1
    return 2


def calculate_heartbeats(shb, chb):
    """
    Given a heartbeat string from the server, and a heartbeat tuple from the client,
    calculate what the actual heartbeat settings should be.

    :param (str,str) shb: server heartbeat numbers
    :param (int,int) chb: client heartbeat numbers

    :rtype: (int,int)
    """
    (sx, sy) = shb
    (cx, cy) = chb
    x = 0
    y = 0
    if cx != 0 and sy != "0":
        x = max(cx, int(sy))
    if cy != 0 and sx != "0":
        y = max(cy, int(sx))
    return x, y

def get_errno(e):
    """
    Return the errno of an exception, or the first argument if errno is not available.

    :param Exception e: the exception object
    """
    try:
        return e.errno
    except AttributeError:
        return e.args[0]
