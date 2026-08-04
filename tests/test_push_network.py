import threading
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch, sentinel

from tigeropen.common.consts import Market
from tigeropen.push.network.connect import BaseConnection, PushConnection
from tigeropen.push.network.exception import ConnectFailedException
from tigeropen.push.network.listener import ConnectionListener, HeartbeatListener, Publisher
from tigeropen.push.network.protocal import Protocol
from tigeropen.push.network import utils
from tigeropen.push.push_client import PushClient
from tigeropen.push.thread_pool import CallbackThreadPoolExecutor, OrderedThreadPoolExecutor

import pytest


# 纯单测：永远不碰真实接口，contract / integ job 会跳过
pytestmark = pytest.mark.unit


class TestPushClientFacade(unittest.TestCase):

    @patch('tigeropen.push.push_client.ProtobufPushClient')
    def test_constructs_protobuf_client_with_all_options(self, mock_client):
        config = sentinel.config
        executor = sentinel.executor
        wrapper = PushClient('host', 9883, use_ssl=False, connection_timeout=17,
                             heartbeats=(1000, 2000), client_config=config,
                             callback_executor=executor)
        self.assertIs(wrapper.client, mock_client.return_value)
        mock_client.assert_called_once_with(
            host='host', port=9883, use_ssl=False, connection_timeout=17,
            heartbeats=(1000, 2000), client_config=config,
            callback_executor=executor,
        )

    @patch('tigeropen.push.push_client.StompPushClient')
    def test_constructs_stomp_client(self, mock_client):
        wrapper = PushClient('host', 9883, use_protobuf=False)
        self.assertIs(wrapper.client, mock_client.return_value)
        mock_client.assert_called_once_with(
            host='host', port=9883, use_ssl=True, connection_timeout=30,
            heartbeats=(10000, 10000),
        )

    def test_callback_properties_delegate_to_underlying_client(self):
        wrapper = PushClient.__new__(PushClient)
        wrapper.client = SimpleNamespace()
        properties = [
            'subscribed_symbols', 'query_subscribed_callback', 'quote_changed',
            'quote_bbo_changed', 'quote_depth_changed', 'tick_changed',
            'stock_top_changed', 'option_top_changed', 'kline_changed',
            'cc_changed', 'cc_bbo_changed', 'full_tick_changed', 'asset_changed',
            'position_changed', 'order_changed', 'transaction_changed',
            'connect_callback', 'disconnect_callback', 'subscribe_callback',
            'unsubscribe_callback', 'error_callback', 'kickout_callback',
        ]
        for name in properties:
            with self.subTest(name=name):
                original = object()
                replacement = object()
                setattr(wrapper.client, name, original)
                self.assertIs(getattr(wrapper, name), original)
                setattr(wrapper, name, replacement)
                self.assertIs(getattr(wrapper.client, name), replacement)

        wrapper.client.on_heartbeat = sentinel.current_heartbeat
        self.assertIs(wrapper.heartbeat_callback, sentinel.current_heartbeat)
        wrapper.heartbeat_callback = sentinel.new_heartbeat
        self.assertIs(wrapper.client.heartbeat_callback, sentinel.new_heartbeat)

    def test_lifecycle_and_subscription_methods_delegate(self):
        wrapper = PushClient.__new__(PushClient)
        wrapper.client = MagicMock()
        wrapper.client.configure_mock(**{
            'subscribe_asset.return_value': 'asset-id',
            'subscribe_position.return_value': 'position-id',
            'subscribe_order.return_value': 'order-id',
            'subscribe_transaction.return_value': 'transaction-id',
            'subscribe_quote.return_value': 'quote-id',
            'subscribe_tick.return_value': 'tick-id',
            'subscribe_depth_quote.return_value': 'depth-id',
            'subscribe_option.return_value': 'option-id',
            'subscribe_future.return_value': 'future-id',
            'query_subscribed_quote.return_value': 'query-id',
            'unsubscribe_quote.return_value': 'unquote-id',
            'unsubscribe_tick.return_value': 'untick-id',
            'subscribe_cc.return_value': 'cc-id',
            'unsubscribe_cc.return_value': 'uncc-id',
        })

        wrapper.connect('id', 'key')
        wrapper.disconnect()
        wrapper.on_connected(sentinel.frame)
        wrapper.on_disconnected()
        wrapper.on_message(sentinel.frame)
        wrapper.on_error(sentinel.frame)
        wrapper.client.connect.assert_called_once_with(tiger_id='id', private_key='key')

        self.assertEqual(wrapper.subscribe_asset('A'), 'asset-id')
        self.assertEqual(wrapper.subscribe_position('A'), 'position-id')
        self.assertEqual(wrapper.subscribe_order('A'), 'order-id')
        self.assertEqual(wrapper.subscribe_transaction('A'), 'transaction-id')
        self.assertEqual(wrapper.subscribe_quote(['AAPL'], ignored=True), 'quote-id')
        self.assertEqual(wrapper.subscribe_tick(['AAPL']), 'tick-id')
        self.assertEqual(wrapper.subscribe_depth_quote(['AAPL']), 'depth-id')
        self.assertEqual(wrapper.subscribe_option(['AAPL  270115C00200000']), 'option-id')
        self.assertEqual(wrapper.subscribe_future(['ES2703']), 'future-id')
        self.assertEqual(wrapper.query_subscribed_quote(), 'query-id')
        self.assertEqual(wrapper.unsubscribe_quote(), 'unquote-id')
        self.assertEqual(wrapper.unsubscribe_tick(), 'untick-id')
        self.assertEqual(wrapper.subscribe_cc(['BTC']), 'cc-id')
        self.assertEqual(wrapper.unsubscribe_cc(), 'uncc-id')
        wrapper.client.subscribe_quote.assert_called_once_with(symbols=['AAPL'])

        self.assertIsNone(wrapper.unsubscribe_asset())
        self.assertIsNone(wrapper.unsubscribe_position())
        self.assertIsNone(wrapper.unsubscribe_order())
        self.assertIsNone(wrapper.unsubscribe_transaction())
        self.assertIsNone(wrapper.unsubscribe_depth_quote(['AAPL']))
        self.assertIsNone(wrapper.subscribe_market('US'))
        self.assertIsNone(wrapper.unsubscribe_market('US'))
        self.assertIsNone(wrapper.subscribe_stock_top(Market.US, ['latest_price']))
        self.assertIsNone(wrapper.unsubscribe_stock_top(Market.US, ['latest_price']))
        self.assertIsNone(wrapper.subscribe_option_top(Market.US, ['delta']))
        self.assertIsNone(wrapper.unsubscribe_option_top(Market.US, ['delta']))
        self.assertIsNone(wrapper.subscribe_kline(['AAPL']))
        self.assertIsNone(wrapper.unsubscribe_kline(['AAPL']))
        wrapper.client.subscribe_stock_top.assert_called_once_with('US', ['latest_price'])
        wrapper.client.unsubscribe_option_top.assert_called_once_with('US', ['delta'])


class TestThreadPool(unittest.TestCase):

    def test_submit_routes_and_shutdown(self):
        self.assertIs(OrderedThreadPoolExecutor, CallbackThreadPoolExecutor)
        with patch('tigeropen.push.thread_pool.os.cpu_count', return_value=2):
            default_pool = CallbackThreadPoolExecutor(0)
        self.assertEqual(default_pool._max_workers, 6)
        default_pool.shutdown()

        pool = CallbackThreadPoolExecutor(2)
        try:
            self.assertEqual(pool.submit(lambda value: value * 2, 3).result(timeout=1), 6)
            self.assertEqual(pool.submit(lambda: 'ok', key='fixed').result(timeout=1), 'ok')
        finally:
            pool.shutdown(wait=True, cancel_futures=True)


class TestNetworkUtils(unittest.TestCase):

    def test_pure_network_helpers(self):
        for command, name in utils.CMD_TYPE_NAME_MAP.items():
            self.assertEqual(utils.get_command_name(command), name)
        self.assertEqual(utils.get_command_name(999), 'unknown')
        self.assertTrue(utils.is_eol_default(b'\n'))
        self.assertFalse(utils.is_eol_default(b'\x00'))
        self.assertEqual(utils.is_localhost(('localhost', 80)), 1)
        self.assertEqual(utils.is_localhost(('example.invalid', 80)), 2)
        self.assertEqual(utils.calculate_heartbeats(('0', '0'), (0, 0)), (0, 0))
        self.assertEqual(utils.calculate_heartbeats(('100', '200'), (50, 60)), (200, 100))
        self.assertEqual(utils.calculate_heartbeats(('0', '200'), (300, 400)), (300, 0))
        self.assertEqual(utils.calculate_heartbeats(('100', '0'), (300, 400)), (0, 400))
        self.assertEqual(utils.get_errno(SimpleNamespace(errno=61)), 61)
        self.assertEqual(utils.get_errno(Exception(62)), 62)

    @patch('tigeropen.push.network.utils.threading.Thread')
    def test_default_create_thread(self, mock_thread_class):
        thread = mock_thread_class.return_value
        result = utils.default_create_thread(sentinel.callback)
        mock_thread_class.assert_called_once_with(None, sentinel.callback)
        self.assertTrue(thread.daemon)
        thread.start.assert_called_once_with()
        self.assertIs(result, thread)


class TestProtocolAndConnections(unittest.TestCase):

    def test_base_connection_delegates_transport_operations(self):
        transport = MagicMock()
        transport.get_listener.return_value = sentinel.listener
        transport.is_connected.return_value = True
        transport.get_ssl.return_value = sentinel.ssl
        connection = BaseConnection(transport)
        connection.disconnect()
        connection.set_listener('name', sentinel.listener)
        connection.remove_listener('name')
        self.assertIs(connection.get_listener('name'), sentinel.listener)
        self.assertTrue(connection.is_connected())
        connection.set_ssl([('host', 443)], cert_file='cert')
        self.assertIs(connection.get_ssl(('host', 443)), sentinel.ssl)
        transport.set_ssl.assert_called_once_with([('host', 443)], cert_file='cert')

    def test_protocol_send_connect_wait_and_disconnect(self):
        transport = MagicMock()
        protocol = Protocol(transport, heartbeats=(1000, 2000))
        transport.set_listener.assert_called_once_with('protocol-listener', protocol)
        protocol.send_frame(sentinel.request)
        transport.transmit.assert_called_with(sentinel.request)

        protocol.connect(sentinel.connect_request, wait=False)
        transport.wait_for_connection.assert_not_called()
        transport.connection_error = False
        protocol.connect(sentinel.connect_request, wait=True)
        transport.wait_for_connection.assert_called_once_with()

        transport.connection_error = True
        with self.assertRaises(ConnectFailedException):
            protocol.connect(sentinel.connect_request, wait=True)

        transport.is_connected.return_value = False
        protocol.disconnect()
        with patch('tigeropen.push.network.protocal.ProtoMessageUtil.build_disconnect_message',
                   return_value=sentinel.disconnect_request):
            transport.is_connected.return_value = True
            protocol.disconnect()
        transport.transmit.assert_called_with(sentinel.disconnect_request)

    @patch('tigeropen.push.network.connect.Transport')
    def test_push_connection_starts_connects_and_stops_transport(self, transport_class):
        transport = transport_class.return_value
        transport.connection_error = False
        transport.is_connected.return_value = True
        connection = PushConnection(host_and_ports=[('host', 9883)], heartbeats=(1, 2),
                                    callback_executor=sentinel.executor)
        self.assertIs(connection.transport, transport)
        connection.connect(sentinel.request, wait=True)
        transport.start.assert_called_once_with()
        transport.transmit.assert_called_with(sentinel.request)
        transport.wait_for_connection.assert_called_once_with()

        with patch('tigeropen.push.network.protocal.ProtoMessageUtil.build_disconnect_message',
                   return_value=sentinel.disconnect_request):
            connection.disconnect()
        transport.transmit.assert_called_with(sentinel.disconnect_request)
        transport.stop.assert_called_once_with()


class TestHeartbeatListener(unittest.TestCase):

    @patch('tigeropen.push.network.listener.utils.default_create_thread')
    @patch('tigeropen.push.network.listener.monotonic', return_value=10)
    @patch('tigeropen.push.network.listener.ProtoMessageUtil.extract_heart_beat', return_value=(2000, 4000))
    def test_connected_initializes_heartbeat_without_real_thread(self, extract, monotonic, create_thread):
        thread = SimpleNamespace(name='Worker')
        create_thread.return_value = thread
        listener = HeartbeatListener(MagicMock(), (0, 0), heart_beat_receive_scale=1.5)
        listener.on_connected(sentinel.frame)
        self.assertTrue(listener.running)
        self.assertEqual(listener.send_sleep, 2)
        self.assertEqual(listener.receive_sleep, 6)
        self.assertEqual(listener.received_heartbeat, 16)
        self.assertEqual(thread.name, 'HeartbeatWorker')

    @patch('tigeropen.push.network.listener.monotonic', side_effect=[20, 30, 40, 50])
    def test_heartbeat_state_callbacks(self, monotonic):
        listener = HeartbeatListener(MagicMock(), (1000, 1000))
        listener.received_heartbeat = 10
        listener.send_sleep = 1
        listener.next_outbound_heartbeat = 15
        listener.on_message(sentinel.frame)
        self.assertEqual(listener.received_heartbeat, 20)
        listener.on_error(sentinel.frame)
        self.assertEqual(listener.received_heartbeat, 30)
        listener.on_heartbeat(sentinel.frame)
        self.assertEqual(listener.received_heartbeat, 40)
        listener.on_send(sentinel.frame)
        self.assertEqual(listener.next_outbound_heartbeat, 51)
        listener.on_disconnecting()
        self.assertTrue(listener.disconnecting)
        listener.on_disconnected()
        self.assertFalse(listener.running)
        self.assertTrue(listener.heartbeat_terminate_event.is_set())

    def test_listener_base_interfaces_are_safe_noops(self):
        publisher = Publisher()
        publisher.set_listener('name', sentinel.listener)
        publisher.remove_listener('name')
        self.assertIsNone(publisher.get_listener('name'))
        listener = ConnectionListener()
        listener.on_connecting(None)
        listener.on_connected(None)
        listener.on_disconnecting()
        listener.on_disconnected()
        listener.on_message(None)
        listener.on_error(None)
        listener.on_send(None)
        listener.on_heartbeat(None)
        listener.on_receiver_loop_completed(None)


if __name__ == '__main__':
    unittest.main()
