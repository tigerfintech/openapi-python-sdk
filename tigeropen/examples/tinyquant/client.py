from tigeropen.trade.trade_client import TradeClient
from tigeropen.push.push_client import PushClient
from tigeropen.quote.quote_client import QuoteClient
from tigeropen.common.consts import Language
from tigeropen.tiger_open_config import TigerOpenClientConfig
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.examples.tinyquant.context import global_context
from tigeropen.examples.tinyquant import setting


def get_client_config():
    """
    https://www.itiger.com/openapi/info 开发者信息获取
    :return:
    """
    client_config = TigerOpenClientConfig(sandbox_debug=setting.IS_SANDBOX)
    client_config.private_key = read_private_key(setting.PRIVATE_KEY)
    client_config.tiger_id = setting.TIGER_ID
    client_config.account = setting.ACCOUNT
    client_config.language = Language.en_US
    return client_config


client_config = get_client_config()

global_context.account = client_config.account

# ============= initialize push client & trade_client & quote_client ===================
protocol, host, port = client_config.socket_host_port
push_client = PushClient(host, port, use_ssl=(protocol == 'ssl'))
trade_client = TradeClient(client_config, logger=None)
quote_client = QuoteClient(client_config, logger=None)