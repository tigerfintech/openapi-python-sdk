from .protocal import *
from .transport import *


class BaseConnection(Publisher):
    """
    Base class for all connection classes.
    """

    def __init__(self, transport):
        """
        :param Transport transport:
        """
        self.transport = transport

    def disconnect(self): pass

    def set_listener(self, name, listener):
        self.transport.set_listener(name, listener)

    def remove_listener(self, name):
        """
        :param str name:
        """
        self.transport.remove_listener(name)

    def get_listener(self, name):
        """
        :param str name:

        :rtype: ConnectionListener
        """
        return self.transport.get_listener(name)

    def is_connected(self):
        """
        :rtype: bool
        """
        return self.transport.is_connected()

    def set_ssl(self, *args, **kwargs):
        self.transport.set_ssl(*args, **kwargs)

    def get_ssl(self, host_and_port=None):
        return self.transport.get_ssl(host_and_port)


class PushConnection(BaseConnection, Protocol):
    """
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
                 heartbeats=(0, 0),
                 keepalive=None,
                 vhost=None,
                 auto_decode=True,
                 encoding="utf-8",
                 heart_beat_receive_scale=1.5,
                 bind_host_port=None):
        transport = Transport(host_and_ports, prefer_localhost, try_loopback_connect,
                              reconnect_sleep_initial, reconnect_sleep_increase, reconnect_sleep_jitter,
                              reconnect_sleep_max, reconnect_attempts_max, timeout,
                              keepalive, vhost, auto_decode, encoding, bind_host_port=bind_host_port)
        BaseConnection.__init__(self, transport)
        Protocol.__init__(self, transport, heartbeats,
                          heart_beat_receive_scale=heart_beat_receive_scale)

    def connect(self, *args, **kwargs):
        self.transport.start()
        Protocol.connect(self, *args, **kwargs)

    def disconnect(self):
        Protocol.disconnect(self)
        self.transport.stop()
