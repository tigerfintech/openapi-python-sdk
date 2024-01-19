"""Provides the underlying transport functionality
"""

import errno
import logging
import math
import random
import struct
import sys
import time
from io import BytesIO
from time import monotonic

from google.protobuf.json_format import MessageToJson

from ..pb.util import ProtoMessageUtil

try:
    from socket import SOL_SOCKET, SO_KEEPALIVE, SOL_TCP, TCP_KEEPIDLE, TCP_KEEPINTVL, TCP_KEEPCNT

    LINUX_KEEPALIVE_AVAIL = True
except ImportError:
    LINUX_KEEPALIVE_AVAIL = False

try:
    from socket import IPPROTO_TCP

    MAC_KEEPALIVE_AVAIL = True
except ImportError:
    MAC_KEEPALIVE_AVAIL = False

try:
    import ssl
    from ssl import SSLError

    DEFAULT_SSL_VERSION = ssl.PROTOCOL_TLS_CLIENT
except (ImportError, AttributeError):
    ssl = None


    class SSLError(object):
        pass


    DEFAULT_SSL_VERSION = None

from . import exception
from .utils import *
from . import listener

PARSING_LEN = 0
PARSING_MSG = 1


def encode_frame(packed_frame):
    value = len(packed_frame)
    header_array = []

    bits = value & 0x7f
    value >>= 7
    while value:
        header_array.append(struct.Struct(">B").pack((0x80 | bits)))
        bits = value & 0x7f
        value >>= 7

    header_array.append(struct.Struct(">B").pack(bits))
    return b"".join(header_array) + packed_frame


def decode_varint(buffer):
    mask = (1 << 32) - 1
    result_type = int
    result = 0
    shift = 0
    for b in buffer:
        result |= ((b & 0x7f) << shift)
        shift += 7
        if shift >= 64:
            raise Exception('Too many bytes when decoding varint.')
    result &= mask
    result = result_type(result)
    return result


class BaseTransport(listener.Publisher):

    def __init__(self, auto_decode=True, encoding="utf-8", is_eol_fc=is_eol_default):
        self.__recvbuf = b""
        self.listeners = {}
        self.running = False
        self.blocking = None
        self.connected = False
        self.connection_error = False
        self.disconnecting = False
        self.__receipts = {}
        self.current_host_and_port = None
        self.bind_host_port = None
        # flag used when we receive the disconnect receipt
        self.__disconnect_receipt = None
        self.notified_on_disconnect = False

        # function for creating threads used by the connection
        self.create_thread_fc = default_create_thread

        self.__listeners_change_condition = threading.Condition()
        self.__receiver_thread_exit_condition = threading.Condition()
        self.__receiver_thread_exited = False
        self.__send_wait_condition = threading.Condition()
        self.__connect_wait_condition = threading.Condition()
        self.__auto_decode = auto_decode
        self.__encoding = encoding
        self.__is_eol = is_eol_fc
        self.__parse_status = PARSING_LEN
        self.__frame_buffer = b""
        self.__frame_len = None

    def override_threading(self, create_thread_fc):
        """
        Override for thread creation. Use an alternate threading library by
        setting this to a function with a single argument (which is the receiver loop callback).
        The thread which is returned should be started (ready to run)

        :param function create_thread_fc: single argument function for creating a thread
        """
        self.create_thread_fc = create_thread_fc

    def start(self):
        """
        Start the connection. This should be called after all
        listeners have been registered. If this method is not called,
        no frames will be received by the connection and no SSL/TLS
        handshake will occur.
        """
        self.running = True
        self.attempt_connection()
        receiver_thread = self.create_thread_fc(self.__receiver_loop)
        logging.debug("created thread %s using func %s", receiver_thread, self.create_thread_fc)
        self.notify(SocketCommon.Command.CONNECT)

    def stop(self):
        """
        Stop the connection. Performs a clean shutdown by waiting for the
        receiver thread to exit.
        """
        with self.__receiver_thread_exit_condition:
            while not self.__receiver_thread_exited and self.is_connected():
                self.__receiver_thread_exit_condition.wait()

    def is_connected(self):
        """
        :rtype: bool
        """
        return self.connected

    def set_connected(self, connected):
        """
        :param bool connected:
        """
        with self.__connect_wait_condition:
            self.connected = connected
            if connected:
                self.disconnecting = False
                self.__connect_wait_condition.notify()

    def set_listener(self, name, listener):
        assert listener is not None
        with self.__listeners_change_condition:
            self.listeners[name] = listener

    def remove_listener(self, name):
        """
        Remove a listener according to the specified name

        :param str name: the name of the listener to remove
        """
        with self.__listeners_change_condition:
            del self.listeners[name]

    def get_listener(self, name):
        """
        Return the named listener

        :param str name: the listener to return

        :rtype: ConnectionListener
        """
        return self.listeners.get(name)

    def process_frame(self, f):
        """
        :param tigeropen.push.pb.Response_pb2.Response f: Frame object
        :param bytes frame_str: raw frame content
        """
        frame = f
        self.notify(frame.command, frame)

    def notify(self, cmd_type, frame=None):
        """
        Utility function for notifying listeners of incoming and outgoing messages
        """
        if cmd_type == SocketCommon.Command.CONNECT:
            self.set_connected(True)

        elif cmd_type == SocketCommon.Command.DISCONNECT:
            self.notified_on_disconnect = True
            self.set_connected(False)

        with self.__listeners_change_condition:
            listeners = sorted(self.listeners.items())

        for (_, listener) in listeners:
            cmd_name = get_command_name(cmd_type)
            notify_func = getattr(listener, "on_%s" % cmd_name, None)
            if not notify_func:
                logging.debug("listener %s has no method on_%s", listener, cmd_name)
                continue
            if cmd_type == SocketCommon.Command.HEARTBEAT:
                notify_func(frame)
                continue
            if cmd_type == SocketCommon.Command.DISCONNECT:
                notify_func()
                continue
            if cmd_type == SocketCommon.Command.CONNECT:
                notify_func(self.current_host_and_port)
                continue

            if cmd_type == SocketCommon.Command.ERROR and not self.connected:
                with self.__connect_wait_condition:
                    self.connection_error = True
                    self.__connect_wait_condition.notify()

            notify_func(frame)

    def transmit(self, frame):
        """
        Convert a frame object to a frame string and transmit to the server.

        """
        with self.__listeners_change_condition:
            listeners = sorted(self.listeners.items())

        for (_, listener) in listeners:
            try:
                listener.on_send(frame)
            except AttributeError:
                continue

        packed_frame = frame.SerializeToString()
        logging.debug("sending frame: %s", MessageToJson(frame))
        encoded_frame = encode_frame(packed_frame)
        self.send(encoded_frame)

    def send(self, encoded_frame):
        """
        Send an encoded frame over this transport (to be implemented in subclasses)

        :param bytes encoded_frame: a Frame object which has been encoded for transmission
        """
        pass

    def receive(self):
        """
        Receive a chunk of data (to be implemented in subclasses)

        :rtype: bytes
        """
        pass

    def cleanup(self):
        """
        Cleanup the transport (to be implemented in subclasses)
        """
        pass

    def attempt_connection(self):
        """
        Attempt to establish a connection.
        """
        pass

    def disconnect_socket(self):
        """
        Disconnect the socket.
        """
        pass

    def wait_for_connection(self, timeout=None):
        """
        Wait until we've established a connection with the server.

        :param float timeout: how long to wait, in seconds
        """
        if timeout is not None:
            wait_time = timeout / 10.0
        else:
            wait_time = None
        with self.__connect_wait_condition:
            while self.running and not self.is_connected() and not self.connection_error:
                self.__connect_wait_condition.wait(wait_time)
        if not self.running or not self.is_connected():
            raise exception.ConnectFailedException()

    def __receiver_loop(self):
        """
        Main loop listening for incoming data.
        """
        logging.debug("starting receiver loop (%s)", threading.current_thread())
        notify_disconnected = True
        try:
            while self.running:
                try:
                    while self.running:
                        frames = self.__read()
                        for frame in frames:
                            self.process_frame(frame)
                except exception.ConnectionClosedException:
                    if self.running:
                        #
                        # Clear out any half-received messages after losing connection
                        #
                        self.__recvbuf = b""
                        self.running = False
                        notify_disconnected = True
                    break
                finally:
                    self.cleanup()
        finally:
            with self.__receiver_thread_exit_condition:
                self.__receiver_thread_exited = True
                self.__receiver_thread_exit_condition.notify_all()
            logging.debug("receiver loop ended")
            if notify_disconnected and not self.notified_on_disconnect:
                self.notify(SocketCommon.Command.DISCONNECT)
            with self.__connect_wait_condition:
                self.__connect_wait_condition.notify_all()
            self.notified_on_disconnect = False

    def __read(self):
        """
        Read the next frame(s) from the socket.

        :return: list of frames read
        :rtype: list(bytes)
        """
        fastbuf = BytesIO()
        while self.running:
            try:
                try:
                    c = self.receive()
                except exception.InterruptedException:
                    logging.debug("socket read interrupted, restarting")
                    continue
            except Exception:
                logging.debug("socket read error", exc_info=True)
                c = b""
            if c is None or len(c) == 0:
                logging.debug("nothing received, raising CCE")
                raise exception.ConnectionClosedException()
            fastbuf.write(c)
            break
        self.__recvbuf += fastbuf.getvalue()
        fastbuf.close()
        result = []

        if self.__recvbuf and self.running:
            for b in self.__recvbuf:
                if self.__parse_status == PARSING_LEN:
                    self.__frame_buffer += struct.Struct(">B").pack(b)
                    if not (b & 0x80):
                        self.__frame_len = decode_varint(self.__frame_buffer)
                        self.__parse_status = PARSING_MSG
                        self.__frame_buffer = b""
                        continue
                elif self.__parse_status == PARSING_MSG:
                    self.__frame_buffer += struct.Struct(">B").pack(b)
                    if len(self.__frame_buffer) == self.__frame_len:
                        frame = ProtoMessageUtil.parse_response_message(self.__frame_buffer)
                        result.append(frame)
                        self.__frame_buffer = b""
                        self.__frame_len = 0
                        self.__parse_status = PARSING_LEN
            self.__recvbuf = b""
        return result


class Transport(BaseTransport):
    """
    Represents a client 'transport'. Effectively this is the communications mechanism without the definition of
    the protocol.

    :param list((str,int)) host_and_ports: a list of (host, port) tuples
    :param bool prefer_localhost: if True and the local host is mentioned in the (host,
        port) tuples, try to connect to this first
    :param bool try_loopback_connect: if True and the local host is found in the host
        tuples, try connecting to it using loopback interface
        (127.0.0.1)
    :param float reconnect_sleep_initial: initial delay in seconds to wait before reattempting
        to establish a connection if connection to any of the
        hosts fails.
    :param float reconnect_sleep_increase: factor by which the sleep delay is increased after
        each connection attempt. For example, 0.5 means
        to wait 50% longer than before the previous attempt,
        1.0 means wait twice as long, and 0.0 means keep
        the delay constant.
    :param float reconnect_sleep_max: maximum delay between connection attempts, regardless
        of the reconnect_sleep_increase.
    :param float reconnect_sleep_jitter: random additional time to wait (as a percentage of
        the time determined using the previous parameters)
        between connection attempts in order to avoid
        stampeding. For example, a value of 0.1 means to wait
        an extra 0%-10% (randomly determined) of the delay
        calculated using the previous three parameters.
    :param int reconnect_attempts_max: maximum attempts to reconnect (Can also be used for infinite attempts : `-1`)
    :param timeout: the timeout value to use when connecting the socket
    :param keepalive: some operating systems support sending the occasional heart
        beat packets to detect when a connection fails.  This
        parameter can either be set set to a boolean to turn on the
        default keepalive options for your OS, or as a tuple of
        values, which also enables keepalive packets, but specifies
        options specific to your OS implementation.
        For linux, supply ("linux", ka_idle, ka_intvl, ka_cnt)
        For macos, supply ("mac", ka_intvl)
    :param str vhost: specify a virtual hostname to provide in the 'host' header of the connection
    :param int recv_bytes: the number of bytes to use when calling recv
    """

    def __init__(self,
                 host_and_ports=None,
                 prefer_localhost=True,
                 try_loopback_connect=True,
                 reconnect_sleep_initial=0.1,
                 reconnect_sleep_increase=0.5,
                 reconnect_sleep_jitter=0.1,
                 reconnect_sleep_max=60.0,
                 reconnect_attempts_max=3,
                 timeout=None,
                 keepalive=None,
                 vhost=None,
                 auto_decode=True,
                 encoding="utf-8",
                 recv_bytes=1024,
                 is_eol_fc=is_eol_default,
                 bind_host_port=None):
        BaseTransport.__init__(self, auto_decode, encoding, is_eol_fc)

        if host_and_ports is None:
            logging.debug("no hosts_and_ports specified, adding default localhost")
            host_and_ports = [("localhost", 61613)]

        sorted_host_and_ports = []
        sorted_host_and_ports.extend(host_and_ports)

        #
        # If localhost is preferred, make sure all (host, port) tuples that refer to the local host come first in
        # the list
        #
        if prefer_localhost:
            sorted_host_and_ports.sort(key=is_localhost)

        #
        # If the user wishes to attempt connecting to local ports using the loopback interface, for each (host, port)
        # tuple referring to a local host, add an entry with the host name replaced by 127.0.0.1 if it doesn't
        # exist already
        #
        loopback_host_and_ports = []
        if try_loopback_connect:
            for host_and_port in sorted_host_and_ports:
                if is_localhost(host_and_port) == 1:
                    port = host_and_port[1]
                    if not (("127.0.0.1", port) in sorted_host_and_ports or (
                            "localhost", port) in sorted_host_and_ports):
                        loopback_host_and_ports.append(("127.0.0.1", port))

        #
        # Assemble the final, possibly sorted list of (host, port) tuples
        #
        self.__host_and_ports = []
        self.__host_and_ports.extend(loopback_host_and_ports)
        self.__host_and_ports.extend(sorted_host_and_ports)
        self.__bind_host_port = bind_host_port

        self.__reconnect_sleep_initial = reconnect_sleep_initial
        self.__reconnect_sleep_increase = reconnect_sleep_increase
        self.__reconnect_sleep_jitter = reconnect_sleep_jitter
        self.__reconnect_sleep_max = reconnect_sleep_max
        self.__reconnect_attempts_max = reconnect_attempts_max
        self.__timeout = timeout

        self.socket = None
        self.__socket_semaphore = threading.BoundedSemaphore(1)
        self.current_host_and_port = None

        # setup SSL
        self.__ssl_params = {}
        self.__keepalive = keepalive
        self.vhost = vhost
        self.__recv_bytes = recv_bytes

    def is_connected(self):
        """
        Return true if the socket managed by this connection is connected

        :rtype: bool
        """
        try:
            return self.socket is not None and self.socket.getsockname()[1] != 0 and BaseTransport.is_connected(self)
        except socket.error:
            return False

    def disconnect_socket(self):
        """
        Disconnect the underlying socket connection
        """
        self.running = False
        if self.socket is not None:
            if self.__need_ssl():
                #
                # Even though we don't want to use the socket, unwrap is the only API method which does a proper SSL
                # shutdown
                #
                try:
                    self.socket = self.socket.unwrap()
                except Exception:
                    #
                    # unwrap seems flaky on Win with the back-ported ssl mod, so catch any exception and log it
                    #
                    _, e, _ = sys.exc_info()
                    logging.warning(e)
            elif hasattr(socket, "SHUT_RDWR"):
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except socket.error:
                    _, e, _ = sys.exc_info()
                    # ignore when socket already closed
                    if get_errno(e) != errno.ENOTCONN:
                        logging.warning("unable to issue SHUT_RDWR on socket because of error '%s'", e)

        #
        # split this into a separate check, because sometimes the socket is nulled between shutdown and this call
        #
        if self.socket is not None:
            try:
                self.socket.close()
            except socket.error:
                _, e, _ = sys.exc_info()
                logging.warning("unable to close socket because of error '%s'", e)
        self.current_host_and_port = None
        self.socket = None

    def send(self, encoded_frame):
        """
        :param bytes encoded_frame:
        """
        if self.socket is not None:
            try:
                with self.__socket_semaphore:
                    self.socket.sendall(encoded_frame)
            except Exception:
                _, e, _ = sys.exc_info()
                logging.error("error sending frame", exc_info=True)
                raise e
        else:
            raise exception.NotConnectedException()

    def receive(self):
        """
        :rtype: bytes
        """
        try:
            return self.socket.recv(self.__recv_bytes)
        except socket.error:
            _, e, _ = sys.exc_info()
            if get_errno(e) in (errno.EAGAIN, errno.EINTR):
                logging.debug("socket read interrupted, restarting")
                raise exception.InterruptedException()
            if self.is_connected():
                raise

    def cleanup(self):
        """
        Close the socket and clear the current host and port details.
        """
        try:
            self.socket.close()
        except:
            pass  # ignore errors when attempting to close socket
        self.socket = None

    def __enable_keepalive(self):
        def try_setsockopt(sock, name, fam, opt, val=None):
            if val is None:
                return True  # no value to set always works
            try:
                sock.setsockopt(fam, opt, val)
                logging.debug("keepalive: set %r option to %r on socket", name, val)
            except:
                logging.error("keepalive: unable to set %r option to %r on socket", name, val)
                return False
            return True

        ka = self.__keepalive

        if not ka:
            return

        if ka is True:
            ka_sig = "auto"
            ka_args = ()
        else:
            try:
                ka_sig = ka[0]
                ka_args = ka[1:]
            except Exception:
                logging.error("keepalive: bad specification %r", ka)
                return

        if ka_sig == "auto":
            if LINUX_KEEPALIVE_AVAIL:
                ka_sig = "linux"
                ka_args = None
                logging.debug("keepalive: autodetected linux-style support")
            elif MAC_KEEPALIVE_AVAIL:
                ka_sig = "mac"
                ka_args = None
                logging.debug("keepalive: autodetected mac-style support")
            else:
                logging.error("keepalive: unable to detect any implementation, DISABLED!")
                return

        if ka_sig == "linux":
            logging.debug("keepalive: activating linux-style support")
            if ka_args is None:
                logging.debug("keepalive: using system defaults")
                ka_args = (None, None, None)
            ka_idle, ka_intvl, ka_cnt = ka_args
            if try_setsockopt(self.socket, "enable", SOL_SOCKET, SO_KEEPALIVE, 1):
                try_setsockopt(self.socket, "idle time", SOL_TCP, TCP_KEEPIDLE, ka_idle)
                try_setsockopt(self.socket, "interval", SOL_TCP, TCP_KEEPINTVL, ka_intvl)
                try_setsockopt(self.socket, "count", SOL_TCP, TCP_KEEPCNT, ka_cnt)
        elif ka_sig == "mac":
            logging.debug("keepalive: activating mac-style support")
            if ka_args is None:
                logging.debug("keepalive: using system defaults")
                ka_args = (3,)
            ka_intvl = ka_args
            if try_setsockopt(self.socket, "enable", SOL_SOCKET, SO_KEEPALIVE, 1):
                try_setsockopt(self.socket, socket.IPPROTO_TCP, 0x10, ka_intvl)
        else:
            logging.error("keepalive: implementation %r not recognized or not supported", ka_sig)

    def attempt_connection(self):
        """
        Try connecting to the (host, port) tuples specified at construction time.
        """
        self.connection_error = False
        sleep_exp = 1
        connect_count = 0

        logging.debug("attempt reconnection (%s, %s, %s)", self.running, self.socket, connect_count)
        while self.running and self.socket is None and (connect_count < self.__reconnect_attempts_max or
                                                        self.__reconnect_attempts_max == -1):
            for host_and_port in self.__host_and_ports:
                try:
                    logging.debug("attempting connection to host %s, port %s", host_and_port[0], host_and_port[1])
                    if self.__bind_host_port:
                        self.socket = socket.create_connection(host_and_port, self.__timeout, self.__bind_host_port)
                    else:
                        self.socket = socket.create_connection(host_and_port, self.__timeout)
                    self.__enable_keepalive()
                    need_ssl = self.__need_ssl(host_and_port)

                    if need_ssl:  # wrap socket
                        ssl_params = self.get_ssl(host_and_port)
                        tls_context = ssl.SSLContext(DEFAULT_SSL_VERSION)
                        if ssl_params["ca_certs"]:
                            cert_validation = ssl.CERT_REQUIRED
                            tls_context.load_verify_locations(ssl_params["ca_certs"])
                        else:
                            cert_validation = ssl.CERT_NONE
                        if tls_context:
                            # Wrap the socket for TLS
                            certfile = ssl_params["cert_file"]
                            keyfile = ssl_params["key_file"]
                            password = ssl_params.get("password")
                            if certfile and not keyfile:
                                keyfile = certfile
                            if certfile:
                                tls_context.load_cert_chain(certfile, keyfile, password)
                            if cert_validation is None or cert_validation == ssl.CERT_NONE:
                                tls_context.check_hostname = False
                            tls_context.verify_mode = cert_validation
                            logging.debug("wrapping SSL socket")
                            self.socket = tls_context.wrap_socket(self.socket, server_hostname=host_and_port[0])
                        else:
                            # Old-style wrap_socket where we don't have a modern SSLContext (so no SNI)
                            logging.debug("wrapping SSL socket (old style)")
                            self.socket = ssl.wrap_socket(
                                self.socket,
                                keyfile=ssl_params["key_file"],
                                certfile=ssl_params["cert_file"],
                                cert_reqs=cert_validation,
                                ca_certs=ssl_params["ca_certs"],
                                ssl_version=ssl_params["ssl_version"])

                    self.socket.settimeout(self.__timeout)

                    if self.blocking is not None:
                        self.socket.setblocking(self.blocking)

                    #
                    # Validate server cert
                    #
                    if need_ssl and ssl_params["cert_validator"]:
                        cert = self.socket.getpeercert()
                        (ok, errmsg) = ssl_params["cert_validator"](cert, host_and_port[0])
                        if not ok:
                            raise SSLError("Server certificate validation failed: %s", errmsg)

                    self.current_host_and_port = host_and_port
                    logging.info("established connection to host %s, port %s", host_and_port[0], host_and_port[1])
                    break
                except (OSError, AssertionError):
                    self.socket = None
                    connect_count += 1
                    logging.warning("could not connect to host %s, port %s", host_and_port[0], host_and_port[1],
                                    exc_info=True)

            if self.socket is None:
                sleep_duration = (min(self.__reconnect_sleep_max,
                                      ((self.__reconnect_sleep_initial / (1.0 + self.__reconnect_sleep_increase))
                                       * math.pow(1.0 + self.__reconnect_sleep_increase, sleep_exp)))
                                  * (1.0 + random.random() * self.__reconnect_sleep_jitter))
                sleep_end = monotonic() + sleep_duration
                logging.debug("sleeping for %.1f seconds before attempting reconnect", sleep_duration)
                while self.running and monotonic() < sleep_end:
                    time.sleep(0.2)

                if sleep_duration < self.__reconnect_sleep_max:
                    sleep_exp += 1

        if not self.socket:
            raise exception.ConnectFailedException()

    def set_ssl(self,
                for_hosts=[],
                key_file=None,
                cert_file=None,
                ca_certs=None,
                cert_validator=None,
                ssl_version=DEFAULT_SSL_VERSION,
                password=None):
        """
        Sets up SSL configuration for the given hosts. This ensures socket is wrapped in a SSL connection, raising an
        exception if the SSL module can't be found.

        :param for_hosts: a list of tuples describing hosts this SSL configuration should be applied to
        :param cert_file: the path to a X509 certificate
        :param key_file: the path to a X509 key file
        :param ca_certs: the path to the a file containing CA certificates to validate the server against.
                         If this is not set, server side certificate validation is not done.
        :param cert_validator: function which performs extra validation on the client certificate, for example
                               checking the returned certificate has a commonName attribute equal to the
                               hostname (to avoid man in the middle attacks).
                               The signature is: (OK, err_msg) = validation_function(cert, hostname)
                               where OK is a boolean, and cert is a certificate structure
                               as returned by ssl.SSLSocket.getpeercert()
        :param ssl_version: SSL protocol to use for the connection. This should be one of the PROTOCOL_x
                            constants provided by the ssl module. The default is ssl.PROTOCOL_TLSv1
        :param password: SSL password
        """
        if not ssl:
            raise Exception("SSL connection requested, but SSL library not found")

        for host_port in for_hosts:
            self.__ssl_params[host_port] = dict(key_file=key_file,
                                                cert_file=cert_file,
                                                ca_certs=ca_certs,
                                                cert_validator=cert_validator,
                                                ssl_version=ssl_version,
                                                password=password)

    def __need_ssl(self, host_and_port=None):
        """
        Whether current host needs SSL or not.

        :param (str,int) host_and_port: the host/port pair to check, default current_host_and_port
        """
        if not host_and_port:
            host_and_port = self.current_host_and_port

        return host_and_port in self.__ssl_params

    def get_ssl(self, host_and_port=None):
        """
        Get SSL params for the given host.

        :param (str,int) host_and_port: the host/port pair we want SSL params for, default current_host_and_port
        """
        if not host_and_port:
            host_and_port = self.current_host_and_port

        return self.__ssl_params.get(host_and_port)
