# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import base64
import json
import logging
import os
import time
import uuid

from jproperties import Properties
from pytz import timezone
from tigeropen import __VERSION__
from tigeropen.common.consts import Language, ServiceType, License
from tigeropen.common.consts.params import ACCOUNT, LICENSE, PRIVATE_KEY, TIGER_ID, ENV, DATA, TOKEN, SECRET_KEY
from tigeropen.common.util.account_util import AccountUtil
from tigeropen.common.util.common_utils import get_enum_value
from tigeropen.common.util.signature_utils import read_private_key
from tigeropen.common.util.web_utils import do_get

# 环境变量前缀
ENV_PREFIX = 'TIGEROPEN_'
TIGEROPEN_TIGER_ID = ENV_PREFIX + 'TIGER_ID'
TIGEROPEN_ACCOUNT = ENV_PREFIX + 'ACCOUNT'
TIGEROPEN_SECRET_KEY = ENV_PREFIX + 'SECRET_KEY'
TIGEROPEN_PRIVATE_KEY = ENV_PREFIX + 'PRIVATE_KEY'
TIGEROPEN_PROPS_PATH = ENV_PREFIX + 'PROPS_PATH'

DEFAULT_DOMAIN = 'openapi.tigerfintech.com'
DEFAULT_US_DOMAIN = 'openapi.tradeup.com'
DEFAULT_SANDBOX_DOMAIN = 'openapi-sandbox.tigerfintech.com'
DOMAIN_GARDEN_ADDRESS = 'https://cg.play-analytics.com'

HTTPS_PROTOCAL = 'https://'
SSL_PROTOCAL = 'ssl'
GATEWAY_SUFFIX = '/gateway'
DOMAIN_SEPARATOR = '-'

# 网关地址
SERVER_URL = HTTPS_PROTOCAL + DEFAULT_DOMAIN + GATEWAY_SUFFIX
# socket 域名端口
SOCKET_HOST_PORT = (SSL_PROTOCAL, DEFAULT_DOMAIN, 9883)
# US 网关地址
US_SERVER_URL = HTTPS_PROTOCAL + DEFAULT_US_DOMAIN + GATEWAY_SUFFIX
# US socket 域名端口
US_SOCKET_HOST_PORT = (SSL_PROTOCAL, DEFAULT_US_DOMAIN, 9983)
# 开放平台公钥
TIGER_PUBLIC_KEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNF3G8SoEcCZh2rshUbayDgLLrj6rKgzNMxDL2HS' \
                   'nKcB0+GPOsndqSv+a4IBu9+I3fyBp5hkyMMG2+AXugd9pMpy6VxJxlNjhX1MYbNTZJUT4nudki4uh+LM' \
                   'OkIBHOceGNXjgB+cXqmlUnjlqha/HgboeHSnSgpM3dKSJQlIOsDwIDAQAB'
# 请求签名类型
SIGN_TYPE = 'RSA'
# 请求字符集
CHARSET = 'UTF-8'
# 语言
LANGUAGE = Language.en_US
# 请求超时时间, 单位秒, 默认15s
TIMEOUT = 15

# sandbox 环境配置
SANDBOX_SERVER_URL = HTTPS_PROTOCAL + DEFAULT_SANDBOX_DOMAIN + GATEWAY_SUFFIX
SANDBOX_SOCKET_HOST_PORT = (SSL_PROTOCAL, DEFAULT_SANDBOX_DOMAIN, 9885)
SANDBOX_TIGER_PUBLIC_KEY = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCbm21i11hgAENGd3/f280PSe4g9YGkS3TEXBY' \
                           'MidihTvHHf+tJ0PYD0o3PruI0hl3qhEjHTAxb75T5YD3SGK4IBhHn/Rk6mhqlGgI+bBrBVYaXixm' \
                           'HfRo75RpUUuWACyeqQkZckgR0McxuW9xRMIa2cXZOoL1E4SL4lXKGhKoWbwIDAQAB'

DEFAULT_PROPS_FILE = 'tiger_openapi_config.properties'
DEFAULT_TOKEN_FILE = 'tiger_openapi_token.properties'
TOKEN_REFRESH_DURATION = 0  # seconds
TOKEN_CHECK_INTERVAL = 5 * 60  # seconds

def fallback_get_mac_address():
    return ':'.join(("%012x" % uuid.getnode())[i:i + 2] for i in range(0, 12, 2))

try:
    from getmac import get_mac_address
except ImportError:
    get_mac_address = fallback_get_mac_address


class TigerOpenClientConfig:
    def __init__(self, sandbox_debug=None, enable_dynamic_domain=True, props_path=None):
        # 开发者应用id
        self._tiger_id = ''
        # 授权账户
        self._account = ''
        # is paper account
        self._is_paper = False
        # 开发者应用私钥
        self._private_key = ''
        # account license
        self._license = None
        # 请求签名类型，推荐RSA2
        self._sign_type = SIGN_TYPE
        # 机构交易员专有密钥
        self._secret_key = ''
        # 请求字符集，默认utf-8
        self._charset = CHARSET
        # 语言
        self._language = LANGUAGE
        # timezone
        self._timezone = None
        # 请求读取超时，单位秒，默认15s
        self._timeout = TIMEOUT
        self._sandbox_debug = sandbox_debug
        # subscribed trade tick data, Whether to use the full version of the tick
        self.use_full_tick = False

        # 老虎证券开放平台公钥
        self._tiger_public_key = TIGER_PUBLIC_KEY
        # 老虎证券开放平台网关地址
        self._server_url = SERVER_URL
        self._quote_server_url = SERVER_URL
        self._socket_host_port = SOCKET_HOST_PORT

        self._device_id = self.__get_device_id()
        self._token = None

        self.log_level = None
        self.log_path = None
        self.retry_max_time = 60
        self.retry_max_tries = 5
        
        # token 刷新间隔周期， 单位秒
        self._token_refresh_duration = TOKEN_REFRESH_DURATION
        self.token_check_interval = TOKEN_CHECK_INTERVAL

        self.props_path = None
        # 优先从环境变量加载配置
        self._load_env_vars()
        if not self.props_path and props_path:
            self.props_path = props_path
        if not self.props_path:
            self.props_path = '.'
        self._load_props()
        self._token = self.load_token()

        self.domain_conf = dict()
        self.enable_dynamic_domain = enable_dynamic_domain
        if self._sandbox_debug:
            raise NotImplementedError('Sandbox debug mode is deprecated, please set to False')
        if self.is_us():
            self.server_url = US_SERVER_URL
            self.quote_server_url = US_SERVER_URL
            self.socket_host_port = US_SOCKET_HOST_PORT
        if self.enable_dynamic_domain:
            self.domain_conf = self.query_domains()
            self.refresh_server_info()
        self.inited = False
        self._channel = ''

    @property
    def tiger_id(self):
        return self._tiger_id

    @tiger_id.setter
    def tiger_id(self, value):
        self._tiger_id = value

    @property
    def is_paper(self):
        return self._is_paper

    @is_paper.setter
    def is_paper(self, value):
        self._is_paper = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value
        if AccountUtil.is_paper_account(value):
            self.is_paper = True

    @property
    def license(self):
        return self._license

    @license.setter
    def license(self, value):
        self._license = value

    @property
    def sign_type(self):
        return self._sign_type

    @sign_type.setter
    def sign_type(self, value):
        self._sign_type = value

    @property
    def private_key(self):
        return self._private_key

    @private_key.setter
    def private_key(self, value):
        self._private_key = value

    @property
    def tiger_public_key(self):
        return self._tiger_public_key

    @tiger_public_key.setter
    def tiger_public_key(self, value):
        self._tiger_public_key = value

    @property
    def server_url(self):
        return self._server_url

    @server_url.setter
    def server_url(self, value):
        self._server_url = value

    @property
    def quote_server_url(self):
        return self._quote_server_url

    @quote_server_url.setter
    def quote_server_url(self, value):
        self._quote_server_url = value

    @property
    def socket_host_port(self):
        return self._socket_host_port

    @socket_host_port.setter
    def socket_host_port(self, value):
        self._socket_host_port = value

    @property
    def charset(self):
        return self._charset

    @charset.setter
    def charset(self, value):
        self._charset = value

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, value):
        if isinstance(value, str):
            value = timezone(value)
        self._timezone = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def token_refresh_duration(self):
        return self._token_refresh_duration

    @token_refresh_duration.setter
    def token_refresh_duration(self, value):
        if value and value < 30:
            # 最短刷新间隔为 10 s
            value = 30
        self._token_refresh_duration = value

    @staticmethod
    def __get_device_id():
        """
        获取mac地址作为device_id
        :return:
        """
        device_id = None
        try:
            device_id = get_mac_address()
        except Exception:
            pass
        if not device_id:
            device_id = fallback_get_mac_address()
        return device_id

    def _get_props_path(self, filename):
        if self.props_path is not None:
            if os.path.isdir(self.props_path):
                full_path = os.path.join(self.props_path, filename)
            else:
                dirname = os.path.dirname(self.props_path)
                full_path = os.path.join(dirname, filename)
            return full_path
        return None

    def _load_env_vars(self):
        """
        从环境变量加载配置
        """
        # 读取 props_path
        if os.environ.get(TIGEROPEN_PROPS_PATH):
            self.props_path = os.environ.get(TIGEROPEN_PROPS_PATH)

        # 读取核心配置
        if not self.tiger_id and os.environ.get(TIGEROPEN_TIGER_ID):
            self.tiger_id = os.environ.get(TIGEROPEN_TIGER_ID)

        if not self.private_key and os.environ.get(TIGEROPEN_PRIVATE_KEY):
            private_key_content = os.environ.get(TIGEROPEN_PRIVATE_KEY)
            # 检查是否是文件路径
            if os.path.exists(private_key_content):
                self.private_key = read_private_key(private_key_content)
            else:
                self.private_key = private_key_content

        if not self.account and os.environ.get(TIGEROPEN_ACCOUNT):
            self.account = os.environ.get(TIGEROPEN_ACCOUNT)

        if not self.secret_key and os.environ.get(TIGEROPEN_SECRET_KEY):
            self.secret_key = os.environ.get(TIGEROPEN_SECRET_KEY)

    def _load_props(self):
        """
        从配置文件读取配置
        """
        # 从配置文件读取剩余配置或未在环境变量中指定的配置
        full_path = self._get_props_path(DEFAULT_PROPS_FILE)
        if full_path and os.path.exists(full_path):
            try:
                p = Properties()
                with open(full_path, "rb") as f:
                    p.load(f, "utf-8")
                    if not self.tiger_id:
                        self.tiger_id = getattr(p.get(TIGER_ID), DATA, '')
                    if not self.private_key:
                        self.private_key = getattr(p.get(f'{PRIVATE_KEY}_pk1'), DATA, '')
                        if not self.private_key:
                            self.private_key = getattr(p.get(f'{PRIVATE_KEY}_pk8'), DATA, '')
                    if not self.account:
                        self.account = getattr(p.get(ACCOUNT), DATA, '')
                    if not self.license:
                        self.license = getattr(p.get(LICENSE), DATA, '')
                    if not self._sandbox_debug:
                        is_sandbox_env = getattr(p.get(ENV), DATA, '').upper() == 'SANDBOX'
                        self._sandbox_debug = is_sandbox_env
                    if not self.secret_key:
                        self.secret_key = getattr(p.get(SECRET_KEY), DATA, '')
                    if not self._token:
                        self._token = getattr(p.get(TOKEN), DATA, '')
            except Exception as e:
                logging.error(e, exc_info=True)

    def get_token_path(self):
        return self._get_props_path(DEFAULT_TOKEN_FILE)

    def load_token(self):
        full_path = self.get_token_path()
        if full_path and os.path.exists(full_path):
            try:
                p = Properties()
                with open(full_path, "rb") as f:
                    p.load(f, "utf-8")
                    return getattr(p.get(TOKEN), DATA, '')
            except Exception as e:
                logging.error(e, exc_info=True)

    def store_token(self, token):
        full_path = self.get_token_path()
        if full_path and os.path.exists(full_path):
            try:
                p = Properties()
                with open(full_path, "r+b") as f:
                    if token:
                        self.token = token
                        p['token'] = token
                        p.store(f, encoding='utf-8')
            except Exception as e:
                logging.error(e, exc_info=True)

    def should_token_refresh(self):
        if self.token and self.token_refresh_duration != 0:
            tokeninfo = base64.b64decode(self.token)
            gen_ts, expire_ts = tokeninfo[:27].decode('utf-8').split(',')
            if (int(time.time()) - int(gen_ts) // 1000) > self.token_refresh_duration:
                return True
            return False

    def refresh_server_info(self):
        if self.enable_dynamic_domain and self.domain_conf:
            if self.license:
                self.server_url = self._get_domain_by_type(ServiceType.TRADE, self.license, self.is_paper) \
                    + GATEWAY_SUFFIX
                self.quote_server_url = self._get_domain_by_type(ServiceType.QUOTE, self.license, self.is_paper) \
                    + GATEWAY_SUFFIX

            socket_port = self.domain_conf.get('socket_port')
            self.socket_host_port = (SSL_PROTOCAL, self._get_domain_by_type(ServiceType.COMMON, self.license)
                                     .rpartition(HTTPS_PROTOCAL)[-1], socket_port)

    def query_domains(self):
        """
        domains data like:
        {
            "ret": 0,
            "serverTime": 1650966832923,
            "items": [
                {
                    "openapi": {
                        'socket_port': 9883,
                        'port': 9887,
                        'TBSG-QUOTE': 'https://openapi.tigerfintech.com/hkg-quote',
                        'TBNZ-QUOTE': 'https://openapi.tigerfintech.com/hkg-quote',
                        'TBSG-PAPER': 'https://openapi-sandbox.tigerfintech.com/hkg',
                        'TBNZ-PAPER': 'https://openapi-sandbox.tigerfintech.com/hkg',
                        'TBSG': 'https://openapi.tigerfintech.com/hkg',
                        'TBNZ': 'https://openapi.tigerfintech.com/hkg'
                        'COMMON': 'https://openapi.tigerfintech.com',
                    },
                    "openapi-sandbox": {
                        "socket_port": 9885,
                        "COMMON": "https://openapi-sandbox.tigerfintech.com"
                    }
                }
            ]
        }
        :return: dict
        {
            'socket_port': 9883,
            'port': 9887,
            'TBSG-QUOTE': 'https://openapi.tigerfintech.com/hkg-quote',
            'TBNZ-QUOTE': 'https://openapi.tigerfintech.com/hkg-quote',
            'TBSG-PAPER': 'https://openapi-sandbox.tigerfintech.com/hkg',
            'TBNZ-PAPER': 'https://openapi-sandbox.tigerfintech.com/hkg',
            'TBSG': 'https://openapi.tigerfintech.com/hkg',
            'TBNZ': 'https://openapi.tigerfintech.com/hkg',
            'COMMON': 'https://openapi.tigerfintech.com',
        }
        """
        try:
            url = DOMAIN_GARDEN_ADDRESS
            if self.is_us():
                url += '?appName=tradeup'
            result = json.loads(do_get(url, headers=dict(), params=dict(), timeout=1)) \
                .get('items')
            if result:
                for item in result:
                    conf = item.get('openapi-sandbox', dict()) if self._sandbox_debug else item.get('openapi', dict())
                    if conf:
                        return conf
        except Exception:
            pass

    def _get_domain_by_type(self, service_type, license, is_paper=False):
        """

        :param service_type: tigeropen.common.consts.ServiceType  COMMON/TRADE/QUOTE
        :param license: tigeropen.common.consts.License or str
        :param is_paper:
        :return:
        """
        license_value = get_enum_value(license)
        common_domain = self.domain_conf.get(ServiceType.COMMON.value)
        if service_type != ServiceType.COMMON:
            if service_type == ServiceType.QUOTE:
                key = DOMAIN_SEPARATOR.join((license_value, ServiceType.QUOTE.value))
                return self.domain_conf.get(key, common_domain)
            if is_paper:
                key = DOMAIN_SEPARATOR.join((license_value, 'PAPER'))
                return self.domain_conf.get(key, common_domain)
            else:
                key = license_value
                return self.domain_conf.get(key, common_domain)

        return common_domain

    @property
    def sdk_version(self):
        return __VERSION__

    def is_us(self):
        return self.license and License.TBUS.value == get_enum_value(self.license)


def get_client_config(private_key_path=None, tiger_id=None, account=None, sandbox_debug=False, sign_type=None, timeout=None,
                      language=None, charset=None, server_url=None, socket_host_port=None, secret_key=None,
                      enable_dynamic_domain=True, timezone=None, license=None, props_path=None):
    """
    生成客户端配置
    :param private_key_path: 私钥文件路径, 如 '/Users/tiger/.ssh/rsa_private_key.pem'
    :param tiger_id: 开发者应用 id
    :param account: 授权账户 (必填. 作为发送请求时的默认账户. 不论是环球账户, 综合账户或是模拟账户, 都使用此参数)
    :param sandbox_debug: 是否请求 sandbox 环境
    :param sign_type: 签名类型
    :param timeout: 请求超时时间, 单位秒
    :param language: 语言, 取值为 tigeropen.common.consts.Language 中的枚举类型
    :param charset: 字符集编码
    :param server_url: 网关地址
    :param socket_host_port: 推送长连接的域名端口, 值为协议, 域名, 端口构成的三元组
    :param secret_key: 机构交易员专有密钥 (个人开发者无需指定)
    :param enable_dynamic_domain: 是否初始化时拉取服务域名
    :param timezone:
    :param license: account license, like TBSG/TBNZ
    :param props_path: 配置文件路径, 可以是文件夹路径或文件路径. 优先级: 参数值 > 环境变量TIGEROPEN_PROPS_PATH > 默认值'.'
    :return:
    
    注意: 配置的优先级为：参数值 > 环境变量 > 配置文件
    可使用的环境变量包括：
    - TIGEROPEN_TIGER_ID: 开发者应用ID
    - TIGEROPEN_ACCOUNT: 授权账户
    - TIGEROPEN_PRIVATE_KEY: 私钥内容或私钥文件路径
    - TIGEROPEN_SECRET_KEY: 机构交易员专有密钥
    - TIGEROPEN_PROPS_PATH: 配置文件路径
    """
    config = TigerOpenClientConfig(sandbox_debug=sandbox_debug, enable_dynamic_domain=enable_dynamic_domain,
                                   props_path=props_path)
    config.private_key = read_private_key(private_key_path)
    config.tiger_id = tiger_id
    config.account = account
    if sign_type:
        config.sign_type = sign_type
    if timeout:
        config.timeout = timeout
    if language:
        config.language = language
    if timezone:
        config.timezone = timezone
    if charset:
        config.charset = charset
    if server_url:
        config.server_url = server_url
    if socket_host_port:
        config.socket_host_port = socket_host_port
    if secret_key:
        config.secret_key = secret_key
    if license:
        config.license = license
    return config
