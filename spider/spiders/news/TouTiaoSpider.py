# -*- coding: utf-8 -*-
import re
import time

from pydispatch import dispatcher
from scrapy import Request, signals
from selenium import webdriver

from spider.spiders.news.NewsSpider import NewsSpider
from util import XPathUtil


class TouTiaoSpider(NewsSpider):
    """
    今日头条-财经
    """
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            'spider.middlewares.SeleniumExtMiddleware': 600
        }
    }

    name = "toutiao_news"
    allowed_domains = ["toutiao.com"]

    start_url = "https://www.toutiao.com/ch/news_finance/"

    detail_url = "https://www.toutiao.com"

    start_index = 0

    def __init__(self, *a, **kw):
        super(TouTiaoSpider, self).__init__(*a, **kw)
        chrome_options = webdriver.ChromeOptions()
        # 不打开浏览器窗口
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(executable_path=r'spider/file/chromedriver.exe',
                                        chrome_options=chrome_options)
        # 传递信息,也就是当爬虫关闭时scrapy会发出一个spider_closed的信息,当这个信号发出时就调用closeSpider函数关闭这个浏览器.
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        self.browser.get(self.start_url)
        time.sleep(3)
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        self.browser.execute_script("window.scrollTo(0,0)")
        while True:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(20)
            items = XPathUtil.str_to_selector(self.browser.page_source).xpath("/html/body/div/div[4]/div[2]/div["
                                                                              "2]/div/div/div/ul/li["
                                                                              "@ga_event='article_item_click']")
            if self.start_index == len(items):
                break
            for item in items[self.start_index:]:
                nav = item.xpath("div/div[1]/div/div[1]/a/@href").extract_first()
                out_id = re.findall(r"/(\d+?)/", nav)[0]
                yield Request(
                    self.detail_url + nav,
                    meta={
                        "selenium": True,
                        "out_id": out_id,
                        "title": item.xpath("normalize-space(div/div[1]/div/div[1]/a/text())").extract_first(),
                        "source": item.xpath(
                            "normalize-space(div/div[1]/div/div[2]/div[1]/div/a[2]/text())").extract_first().replace(
                            ' ', '').replace('⋅', '')
                    },
                    dont_filter=True,
                    callback=self.detail
                )
            self.start_index = len(items)

    def detail(self, response):
        if "toutiao.com" in response.url:
            push_date = response.xpath("normalize-space(/html/body/div/div[2]/div[2]/div[1]/div[1]/span[last()])")\
                .extract_first()
            print(
                response.meta.get("out_id"),
                push_date,
                response.meta.get("title"),
                "财经",
                response.meta.get("source"),
                None,
                response.xpath("/html/body/div/div[2]/div[2]/div[1]/div[2]"),
                response.url,
                6
            )
            # self.insert_new(
            #     response.meta.get("out_id"),
            #     push_date,
            #     response.meta.get("title"),
            #     "财经",
            #     response.meta.get("source"),
            #     None,
            #     response.xpath("/html/body/div/div[2]/div[2]/div[1]/div[2]"),
            #     response.url,
            #     6
            # )

    def spider_closed(self):
        self.log("spider closed")
        # 当爬虫退出的时关闭浏览器
        self.browser.quit()

