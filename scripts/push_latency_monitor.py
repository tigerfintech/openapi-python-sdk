# -*- coding: utf-8 -*-
"""
行情推送延迟监控脚本

参考 tigeropen/examples/push_client_demo.py，订阅指定标的的最优报价(BBO)推送，
记录每次收到的 askTimestamp / bidTimestamp、本机接收时的系统时间，以及两者差值
(即推送延迟)，写入日志文件；运行结束后打印延迟统计(min/max/avg/p50/p95/p99)。

配置来源：TIGER_CONFIG_PATH 环境变量指向的目录(含 tiger_openapi_config.properties)。
不在代码中硬编码任何账号路径，运行时通过环境变量指定。

用法示例:
    TIGER_CONFIG_PATH=~/.tigeropen/<profile> .venv/bin/python scripts/push_latency_monitor.py
"""
import logging
import os
import statistics
import threading
import time
from datetime import datetime
from pathlib import Path

from tigeropen.push.pb.QuoteBBOData_pb2 import QuoteBBOData
from tigeropen.push.push_client import PushClient
from tigeropen.tiger_open_config import TigerOpenClientConfig

# ---- 配置 ----
SYMBOLS = ['01810', '02513']
RUN_DURATION_SECONDS = 10 * 60  # 持续运行 10 分钟

LOG_DIR = Path(__file__).resolve().parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f'push_latency_{time.strftime("%Y%m%d_%H%M%S")}.log'

logger = logging.getLogger('push_latency_monitor')
logger.setLevel(logging.INFO)
_formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s')
_file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
_file_handler.setFormatter(_formatter)
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)
logger.addHandler(_file_handler)
logger.addHandler(_console_handler)


class LatencyStats:
    """线程安全的延迟采样收集器 (回调可能在线程池的不同线程中并发触发)"""

    def __init__(self):
        self._lock = threading.Lock()
        self._data = {}  # (symbol, 'ask'/'bid') -> [delay_ms, ...]

    def add(self, symbol, kind, delay_ms):
        with self._lock:
            self._data.setdefault((symbol, kind), []).append(delay_ms)

    def report(self):
        with self._lock:
            snapshot = {k: list(v) for k, v in self._data.items()}
        if not snapshot:
            return '(未收到任何 BBO 推送数据)'
        lines = []
        for (symbol, kind) in sorted(snapshot.keys()):
            values = sorted(snapshot[(symbol, kind)])
            n = len(values)
            if n == 0:
                continue

            def pct(p):
                return values[min(int(n * p), n - 1)]

            over_250 = sum(1 for v in values if v > 250)
            over_250_pct = 100 * over_250 / n

            lines.append(
                f'{symbol} {kind}: n={n} '
                f'min={values[0]} p50={pct(0.5)} p90={pct(0.9)} p95={pct(0.95)} p99={pct(0.99)} max={values[-1]} '
                f'avg={statistics.mean(values):.1f} >250ms={over_250_pct:.1f}%'
            )
        return '\n'.join(lines)


stats = LatencyStats()


def on_quote_bbo_changed(frame: QuoteBBOData):
    """最优报价推送回调：按用户方式 latency = recv_time - min(askTimestamp, bidTimestamp)"""
    recv_ts_ms = int(time.time() * 1000)
    local_time_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    symbol = frame.symbol

    # frame.timestamp 是推送数据本身的时间戳（服务端打的）
    data_ts = frame.timestamp
    data_delay = recv_ts_ms - data_ts if data_ts else None
    if data_delay is not None:
        stats.add(symbol, 'server_ts', data_delay)

    # 收集 ask/bid timestamp
    ask_ts = frame.askTimestamp if (frame.HasField('askTimestamp') and frame.askTimestamp) else None
    bid_ts = frame.bidTimestamp if (frame.HasField('bidTimestamp') and frame.bidTimestamp) else None

    # 分别统计
    if ask_ts:
        stats.add(symbol, 'ask', recv_ts_ms - ask_ts)
    if bid_ts:
        stats.add(symbol, 'bid', recv_ts_ms - bid_ts)

    # 用户方式: min(askTimestamp, bidTimestamp)
    ts_candidates = [t for t in (ask_ts, bid_ts) if t]
    if ts_candidates:
        min_ts = min(ts_candidates)
        max_ts = max(ts_candidates)
        latency_min = recv_ts_ms - min_ts  # 用户方式（取最旧的 → 延迟偏大）
        latency_max = recv_ts_ms - max_ts  # 取最新的 → 更接近真实推送延迟
        stats.add(symbol, 'user_method(min)', latency_min)
        stats.add(symbol, 'fresh_method(max)', latency_max)

    # 日志详情
    parts = [f'symbol={symbol}', f'local_time={local_time_str}', f'recv={recv_ts_ms}']
    if data_ts:
        parts.append(f'svrTs={data_ts} svrDelay={data_delay}')
    if ask_ts:
        ask_time_str = datetime.fromtimestamp(ask_ts / 1000).strftime('%H:%M:%S.%f')[:-3]
        parts.append(f'ask={ask_ts}({ask_time_str}) d={recv_ts_ms - ask_ts}ms p={frame.askPrice}')
    if bid_ts:
        bid_time_str = datetime.fromtimestamp(bid_ts / 1000).strftime('%H:%M:%S.%f')[:-3]
        parts.append(f'bid={bid_ts}({bid_time_str}) d={recv_ts_ms - bid_ts}ms p={frame.bidPrice}')
    if ts_candidates:
        parts.append(f'user_latency(min)={latency_min}ms fresh(max)={latency_max}ms')

    logger.info(' '.join(parts))


def query_subscribed_callback(data):
    logger.info(f'subscribed data: {data}')


def subscribe_callback(frame):
    logger.info(f'subscribe callback: {frame}')


def error_callback(frame):
    logger.error(f'push error: {frame}')


def connect_callback(frame):
    logger.info('connected')


def disconnect_callback():
    """连接断开回调，参考 demo 的重连逻辑"""
    for t in range(1, 200):
        try:
            logger.warning('disconnected, reconnecting')
            push_client.connect(client_config.tiger_id, client_config.private_key)
        except Exception:
            logger.exception('connect failed, retry')
            time.sleep(t)
        else:
            logger.info('reconnect success')
            return
    logger.error('reconnect failed, please check your network')


if __name__ == '__main__':
    props_path = os.environ.get('TIGER_CONFIG_PATH', os.path.expanduser('~/.tigeropen/'))
    client_config = TigerOpenClientConfig(props_path=props_path)
    protocol, host, port = client_config.socket_host_port
    push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))

    push_client.quote_bbo_changed = on_quote_bbo_changed
    push_client.query_subscribed_callback = query_subscribed_callback
    push_client.subscribe_callback = subscribe_callback
    push_client.error_callback = error_callback

    push_client.connect(client_config.tiger_id, client_config.private_key)
    push_client.disconnect_callback = disconnect_callback

    logger.info(f'socket={protocol}://{host}:{port} symbols={SYMBOLS} '
               f'duration={RUN_DURATION_SECONDS}s log_file={LOG_FILE}')
    push_client.subscribe_quote(SYMBOLS)

    try:
        time.sleep(RUN_DURATION_SECONDS)
    except KeyboardInterrupt:
        logger.info('收到中断信号，提前结束')
    finally:
        push_client.disconnect()
        logger.info('已断开连接')
        summary = stats.report()
        # 打印本地系统时间信息
        local_now = datetime.now()
        logger.info(f'本地系统时间: {local_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')
        logger.info('==== 延迟统计汇总 ====\n' + summary)
        logger.info('注: dataDelay = recv_time(本地系统时间) - timestamp(服务端时间)，'
                   '负值说明本地时钟慢于服务端时钟')
        print(f'\n本地系统时间: {local_now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')
        print('\n==== 延迟统计汇总 ====')
        print(summary)
        print('\n注: dataDelay = recv_time(本地系统时间) - timestamp(服务端时间)')
        print('    负值说明本地时钟慢于服务端；askDelay/bidDelay = recv_time - ask/bidTimestamp(交易所报价时间)')
        print(f'详细日志: {LOG_FILE}')
