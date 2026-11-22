import json
from unittest.mock import patch

import pytest

from tests.support import client_config
from tigeropen.common.consts import TradingSessionType
from tigeropen.common.util.contract_utils import stock_contract
from tigeropen.trade.domain.order import Order
from tigeropen.trade.trade_client import TradeClient

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('account', ['600021175417', '20220101000000001'])
@pytest.mark.parametrize('method', ['place_order', 'preview_order'])
@pytest.mark.parametrize('session', [TradingSessionType.PRE_RTH, TradingSessionType.RTH_POST,
                                     'PRE_RTH', 'RTH_POST'])
def test_new_trading_sessions_reach_order_payload(account, method, session):
    client = TradeClient(client_config())
    order = Order(account, stock_contract('AAPL', 'USD'), 'BUY', order_type='LMT',
                  quantity=1, limit_price=100, outside_rth=True, trading_session_type=session)
    with patch.object(client, '_TradeClient__fetch_data', return_value=None) as fetch:
        getattr(client, method)(order)
    request = fetch.call_args.args[0].get_params()
    payload = json.loads(request['biz_content'])
    assert request['method'] == method
    assert payload['trading_session_type'] == getattr(session, 'value', session)
    assert payload['outside_rth'] is True
    assert 'tradingSessionType' not in payload
