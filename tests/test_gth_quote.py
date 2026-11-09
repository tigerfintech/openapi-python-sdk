from unittest.mock import MagicMock

import pytest

from tests.support import client_config
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_chains_response import OptionChainsResponse
from tigeropen.push.pb.QuoteData_pb2 import QuoteData
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.pb.util import convert_to_basic_data

# Produced from stock-openapi feat_gth commit 33df7142f.
GTH_WIRE = bytes.fromhex("0a185350585720323032363037323320373338302e3020505554100118a4fb9df1f83331000000000000f83f3889fa9df1f833499a9999999999f13f500e5900000000000029407a095072654d61726b6574e9010000000000001c40f001d00ff901000000008087c340820203475448")
GTH_0a185350585720323032363037323320373338302e3020505554100118a4fb9df1f8333100000000000000003800499a9999999999f13f50005900000000000000007a095072654d61726b6574e9010000000000000000f001d00ff901000000008087c340820203475448_WIRE = bytes.fromhex("0a185350585720323032363037323320373338302e3020505554100118a4fb9df1f8333100000000000000003800499a9999999999f13f50005900000000000000007a095072654d61726b6574e9010000000000000000f001d00ff901000000008087c340820203475448")


@pytest.mark.parametrize("wire,price,trade_time,volume,amount", [
    (GTH_WIRE, 1.5, 1784796380425, 7, 12.5),
    (GTH_0a185350585720323032363037323320373338302e3020505554100118a4fb9df1f8333100000000000000003800499a9999999999f13f50005900000000000000007a095072654d61726b6574e9010000000000000000f001d00ff901000000008087c340820203475448_WIRE, 0, 0, 0, 0),
])
def test_server_gth_wire_survives_basic_callback_conversion(wire, price, trade_time, volume, amount):
    quote = QuoteData.FromString(wire)
    basic = convert_to_basic_data(quote)
    for data in (quote, basic):
        assert data.symbol == "SPXW 20260723 7380.0 PUT"
        for field, value in {"latestPrice": price, "latestPriceTimestamp": trade_time,
                             "preClose": 1.1, "volume": volume, "volumeDecimal": volume,
                             "amount": amount, "cumVolume": 1000, "cumAmount": 9999,
                             "session": "GTH", "hourTradingTag": "PreMarket"}.items():
            assert data.HasField(field) and getattr(data, field) == value
        assert "hourTrading" not in data.DESCRIPTOR.fields_by_name
        assert "HourTrading" not in data.DESCRIPTOR.nested_types_by_name


def test_basic_conversion_keeps_missing_trade_fields_and_session_absent():
    quote = QuoteData(symbol="AAPL", type=SocketCommon.BASIC)
    basic = convert_to_basic_data(quote)
    for field in ("latestPrice", "latestPriceTimestamp", "latestTime", "preClose",
                  "volume", "volumeDecimal", "amount", "cumVolume", "cumAmount",
                  "session", "hourTradingTag"):
        assert not basic.HasField(field)


@pytest.mark.parametrize("flag", [None, True, False])
def test_kline_flag_reaches_every_wire_query(flag):
    client = QuoteClient(client_config(), is_grab_permission=False)
    client._QuoteClient__fetch_data = MagicMock(return_value={"code": 0, "data": []})
    client.get_option_bars(["SPXW  260723P07380000", "SPXW  260723C07380000"],
                           period="5min", with_hour_trading=flag)
    queries = client._QuoteClient__fetch_data.call_args.args[0].biz_model.to_openapi_dict()["option_query"]
    assert len(queries) == 2
    for query in queries:
        if flag is None:
            assert "with_hour_trading" not in query
        else:
            assert query["with_hour_trading"] is flag


@pytest.mark.parametrize("response_type", [OptionBriefsResponse, OptionChainsResponse])
def test_http_nested_gth_fields_and_null(response_type):
    item = {"identifier": "SPXW  260723P07380000", "right": "PUT", "cumVolume": 0,
            "cumAmount": 0.0, "hourTrading": {"session": "GTH", "latestTimestamp": 1784796380425,
                                             "latestPrice": 1.5, "volume": 0}}
    data = [item] if response_type is OptionBriefsResponse else [
        {"symbol": "SPXW", "expiry": 1784779200000, "items": [{"put": item}]}]
    response = response_type()
    response.parse_response_content({"code": 0, "data": data})
    frame = response.briefs if response_type is OptionBriefsResponse else response.chain
    assert frame.iloc[0]["cum_volume"] == 0
    assert frame.iloc[0]["hour_trading"]["latest_timestamp"] == 1784796380425
    assert frame.iloc[0]["hour_trading"]["volume"] == 0

    item["hourTrading"] = None
    response.parse_response_content({"code": 0, "data": data})
    frame = response.briefs if response_type is OptionBriefsResponse else response.chain
    assert "hour_trading" not in frame.columns
