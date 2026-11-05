# -*- coding: utf-8 -*-
"""资讯条目 — news_stock_list 与 news_highlight_list 共用。"""


class NewsItem:
    """单条资讯。

    服务端出参为 camelCase（pubTimestamp），SDK 侧属性为 snake_case，
    由 NewsListResponse 解析时经 camel_to_underline 转换。
    """

    def __init__(self):
        self.id = None             # 文章 ID（highlight 游标翻页 last_id 的取值来源）
        self.title = None          # 标题
        self.summary = None        # 摘要
        self.pub_timestamp = None  # 发布时间戳（秒级）
        self.url = None            # 详情页 URL

    def __repr__(self):
        return 'NewsItem(%s)' % self.__dict__
