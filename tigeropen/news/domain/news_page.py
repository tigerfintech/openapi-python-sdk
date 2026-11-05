# -*- coding: utf-8 -*-
"""资讯列表分页信封 — news_stock_list 与 news_highlight_list 共用。"""


class NewsPage:
    """资讯列表分页结果。

    - items: List[NewsItem]
    - page_count / page_size / total_page / total_size: 分页信封字段
    - highlight 接口翻页只走 last_id 游标：取上一页 items 最后一条的 id
      作为下一次调用的 last_id；不传从最新开始
    """

    def __init__(self):
        self.items = []
        self.page_count = None
        self.page_size = None
        self.total_page = None
        self.total_size = None

    def __repr__(self):
        return 'NewsPage(%s)' % self.__dict__
