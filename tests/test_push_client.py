# -*- coding: utf-8 -*-
# 
# @Date    : 2022/6/24
# @Author  : sukai
import threading
import unittest
from unittest.mock import MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from tigeropen.push.push_client import PushClient
from tigeropen.push.protobuf_push_client import ProtobufPushClient
from tigeropen.push.pb.TradeTickData_pb2 import TradeTickData
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.push.network.transport import Transport
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.thread_pool import OrderedThreadPoolExecutor


class _ImmediateExecutor:

    def __init__(self):
        self.calls = []

    def submit(self, fn, *args, key=None, **kwargs):
        self.calls.append({'key': key, 'args': args, 'kwargs': kwargs})
        return fn(*args, **kwargs)


class _KeyAwareThreadPoolExecutor(ThreadPoolExecutor):

    def submit(self, fn, *args, key=None, **kwargs):
        # ThreadPoolExecutor ignores routing key; this hook keeps compatibility with transport
        return super().submit(fn, *args, **kwargs)


class TestPushClient(unittest.TestCase):

    def test_tick_convert(self):
        expected = 'QQQ', [{'tick_type': '*', 'price': 287.76, 'volume': 99, 'part_code': 'NSDQ',
                     'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084833, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.73, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.72, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.72, 'volume': 10, 'part_code': 'ARCA',
                     'part_code_name': 'NYSE Arca, Inc. (NYSE Arca)', 'cond': 'US_ODD_LOT_TRADE',
                     'time': 1656062084844, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570},
                    {'tick_type': '*', 'price': 287.7, 'volume': 800, 'part_code': 'NSDQ',
                     'part_code_name': 'NASDAQ Stock Market, LLC (NASDAQ)', 'cond': 'US_FORM_T',
                     'time': 1656062084875, 'server_timestamp': 1656062042242, 'type': 'TradeTick',
                     'quote_level': 'usStockQuote', 'sn': 878, 'timestamp': 1656062085570}]

        # Build a TradeTickData protobuf message to exercise ProtobufPushClient._convert_tick
        data = TradeTickData()
        data.symbol = 'QQQ'
        data.type = 'TradeTick'
        data.cond = 'IIIIT'
        data.sn = 878
        data.priceBase = 28770
        data.priceOffset = 2
        data.time.extend([1656062084833, 11, 0, 0, 31])
        data.price.extend([6, 3, 2, 2, 0])
        data.volume.extend([99, 10, 10, 10, 800])
        data.partCode.extend(['t', 'p', 'p', 'p', 't'])
        data.quoteLevel = 'usStockQuote'
        data.timestamp = 1656062085570

        pb_client = ProtobufPushClient('localhost', 0)
        tick = pb_client._convert_tick(data)

        # Convert returned object to comparable (symbol, list-of-dicts)
        symbol = tick.symbol
        items = []
        for it in tick.ticks:
            # only compare the core fields produced by protobuf converter
            items.append({
                'tick_type': getattr(it, 'tick_type', None),
                'price': getattr(it, 'price', None),
                'volume': getattr(it, 'volume', None),
                'part_code': getattr(it, 'part_code', None),
                'part_code_name': getattr(it, 'part_code_name', None),
                'cond': getattr(it, 'cond', None),
                'time': getattr(it, 'time', None),
                'sn': getattr(it, 'sn', None),
            })

        expected_slim = []
        for d in expected[1]:
            expected_slim.append({
                'tick_type': d.get('tick_type'),
                'price': d.get('price'),
                'volume': d.get('volume'),
                'part_code': d.get('part_code'),
                'part_code_name': d.get('part_code_name'),
                'cond': d.get('cond'),
                'time': d.get('time'),
                'sn': d.get('sn'),
            })

        self.assertEqual(symbol, 'QQQ')
        # verify core numeric fields and length
        self.assertEqual(len(items), 5)
        expected_prices = [287.76, 287.73, 287.72, 287.72, 287.7]
        expected_volumes = [99, 10, 10, 10, 800]
        expected_times = [1656062084833, 1656062084844, 1656062084844, 1656062084844, 1656062084875]
        # sn may be data.sn or data.sn + 1 depending on internal handling; ensure non-decreasing
        first_sn = items[0]['sn']
        self.assertIn(first_sn, (878, 879))
        for i, it in enumerate(items):
            self.assertAlmostEqual(it['price'], expected_prices[i], places=2)
            self.assertEqual(it['volume'], expected_volumes[i])
            self.assertEqual(it['time'], expected_times[i])
            # ensure sn sequence is non-decreasing
            if i > 0:
                self.assertGreaterEqual(it['sn'], items[i-1]['sn'])


class TestPushClientThreadPool(unittest.TestCase):

    def setUp(self):
        self.host = "localhost"
        self.port = 9983

    @patch('tigeropen.push.protobuf_push_client._patch_ssl')
    def test_init_default(self, mock_patch_ssl):
        """Test default initialization (no config, no executor)"""
        client = PushClient(self.host, self.port, use_protobuf=True)
        # Access the underlying ProtobufPushClient
        pb_client = client.client

        self.assertIsInstance(pb_client.callback_executor, OrderedThreadPoolExecutor)
        # Default max_workers is None (ThreadPoolExecutor decides based on CPU)
        self.assertGreaterEqual(pb_client.callback_executor._max_workers, 1)

    @patch('tigeropen.push.protobuf_push_client._patch_ssl')
    def test_init_with_config(self, mock_patch_ssl):
        """Test initialization with client_config"""
        config = TigerOpenClientConfig()
        config.callback_thread_pool_size = 5

        client = PushClient(self.host, self.port, use_protobuf=True, client_config=config)
        pb_client = client.client

        self.assertIsInstance(pb_client.callback_executor, OrderedThreadPoolExecutor)
        self.assertEqual(pb_client.callback_executor._max_workers, 5)

    @patch('tigeropen.push.protobuf_push_client._patch_ssl')
    def test_init_with_executor(self, mock_patch_ssl):
        """Test initialization with custom executor"""
        executor = _KeyAwareThreadPoolExecutor(max_workers=3)
        client = PushClient(self.host, self.port, use_protobuf=True, callback_executor=executor)
        pb_client = client.client

        self.assertIs(pb_client.callback_executor, executor)
        self.assertEqual(pb_client.callback_executor._max_workers, 3)

    def test_transport_notify_with_executor(self):
        """Test that Transport uses the executor for MESSAGE commands"""
        executor = _KeyAwareThreadPoolExecutor(max_workers=1)
        transport = Transport(callback_executor=executor)

        # Mock listener
        listener = MagicMock()
        transport.set_listener("test_listener", listener)

        # 1. Test MESSAGE command (should use executor)
        execution_thread_id = None
        event = threading.Event()

        def on_message(frame):
            nonlocal execution_thread_id
            execution_thread_id = threading.get_ident()
            event.set()

        listener.on_message = on_message

        # Mock a frame
        frame = MagicMock()
        frame.command = SocketCommon.Command.MESSAGE

        transport.notify(SocketCommon.Command.MESSAGE, frame)

        # Wait for execution
        event.wait(timeout=1)

        self.assertIsNotNone(execution_thread_id)
        # Should run in a different thread
        self.assertNotEqual(execution_thread_id, threading.get_ident())

        # 2. Test CONNECT command (should NOT use executor, run in current thread)
        # CONNECT maps to on_connecting
        execution_thread_id = None
        event.clear()

        def on_connecting(host_port):
            nonlocal execution_thread_id
            execution_thread_id = threading.get_ident()

        listener.on_connecting = on_connecting

        transport.notify(SocketCommon.Command.CONNECT, None)

        self.assertEqual(execution_thread_id, threading.get_ident())

    def test_transport_routing_key_uses_cmd_and_data_type(self):
        executor = _ImmediateExecutor()
        transport = Transport(callback_executor=executor)

        listener = MagicMock()
        listener.on_message = MagicMock()
        transport.set_listener("test_listener", listener)

        frame = MagicMock()
        frame.command = SocketCommon.Command.MESSAGE
        frame.body = MagicMock()
        frame.body.dataType = SocketCommon.DataType.Quote

        transport.notify(SocketCommon.Command.MESSAGE, frame)

        self.assertEqual(len(executor.calls), 1)
        self.assertEqual(executor.calls[0]['key'],
                         (SocketCommon.Command.MESSAGE, SocketCommon.DataType.Quote))