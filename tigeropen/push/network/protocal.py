from .exception import ConnectFailedException
from .listener import *


class Protocol(HeartbeatListener, ConnectionListener):
    """
    :param transport:
    :param (int,int) heartbeats:
    automatically if it has not been set
    :param float heart_beat_receive_scale: how long to wait for a heartbeat before timing out,
    as a scale factor of receive time
    """

    def __init__(self, transport, heartbeats=(0, 0), heart_beat_receive_scale=1.5):
        HeartbeatListener.__init__(self, transport, heartbeats, heart_beat_receive_scale)
        self.transport = transport
        transport.set_listener("protocol-listener", self)

    def send_frame(self, request):
        """
        Encode and send a frame
        through the underlying transport:
        """
        self.transport.transmit(request)

    def connect(self, request, wait=False):
        """
        Start a connection.
        :param bool wait: if True, wait for the connection to be established/acknowledged
        """
        self.send_frame(request)

        if wait:
            self.transport.wait_for_connection()
            if self.transport.connection_error:
                raise ConnectFailedException()

    def disconnect(self):
        """
        Disconnect from the server.
        """
        if not self.transport.is_connected():
            logging.debug("not sending disconnect, already disconnected")
            return
        self.send_frame(ProtoMessageUtil.build_disconnect_message())
