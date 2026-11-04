from unittest.mock import MagicMock

import pytest

from tests.support import client_config
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.quote.response.option_briefs_response import OptionBriefsResponse
from tigeropen.quote.response.option_chains_response import OptionChainsResponse
from tigeropen.push.pb.QuoteData_pb2 import QuoteData
from tigeropen.push.pb.SocketCommon_pb2 import SocketCommon
from tigeropen.push.pb.util import convert_to_basic_data

# Produced from stock-openapi commit 26fe03848, not the SDK's own schema.
GTH_WIRE = bytes.fromhex("0a185350585720323032363037323320373338302e30205055541001f00100f90100000000000000008202034754488a02310a06e79b98e5898d120347544819000000000000f83f2089fa9df1f8332800310000000000000000399a9999999999f13f")


def test_server_gth_wire_survives_basic_callback_conversion():
    quote = QuoteData.FromString(GTH_WIRE)
    basic = convert_to_basic_data(quote)
    assert basic.symbol == "SPXW 20260723 7380.0 PUT"
    assert basic.HasField("cumVolume") and basic.cumVolume == 0
    assert basic.HasField("cumAmount") and basic.cumAmount == 0
    assert basic.session == "GTH"
    assert basic.hourTrading.tag == "盘前"
    assert basic.hourTrading.latestTimestamp == 1784796380425
    assert basic.hourTrading.latestPrice == 1.5
    assert basic.hourTrading.HasField("volume") and basic.hourTrading.volume == 0
    assert basic.hourTrading.preClose == 1.1
    regular = convert_to_basic_data(QuoteData(symbol="AAPL", type=SocketCommon.BASIC))
    assert not regular.HasField("hourTrading")
    assert not regular.HasField("cumVolume")


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
