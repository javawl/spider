# -*- coding: utf-8 -*-
import re
import json
from scrapy.http.response.html import HtmlResponse
from spider.spiders.BaseSpider import BaseSpider
from scrapy import Request
from spider.spiders.news.NewsSpider import NewsSpider

"""
初创公司  观点  区块链
"""


class TechnodeSpider(NewsSpider):
    custom_settings = {
        "COOKIES_ENABLED": True,
    }

    name = "technode_news"
    allowed_domains = ["cn.technode.com"]


    def start_requests(self):
        yield Request(
            url="https://cn.technode.com/latest/",
            dont_filter=True
        )

    def __init__(self, *a, **kw):
        super(TechnodeSpider, self).__init__(*a, **kw)
        self.browser =None

    def parse(self, response):
        data_list = response.xpath('//div[@class="isotope-system"]/div[@class="isotope-wrapper single-gutter"]//div')
        for data in data_list:
            try:
                #  新闻详情页URl
                url = data.xpath('.//h3[@class="t-entry-title h3"]/a/@href').extract_first()
                # 摘要
                title = data.xpath('.//h3[@class="t-entry-title h3"]/a/text()').extract_first()
                tim = data.xpath('.//p[@class="t-entry-meta"]/span[@class="t-entry-category t-entry-date"]/a/text()').extract_first()
                cover = data.xpath(
                    './/a[@tabindex="-1"]/img/@src').extract_first()
                yield Request(
                    url,
                    meta={"title": title,
                          "tim": tim,
                          "cover": cover
                          },
                    callback=self.detail
                )
            except:
                pass

    #
    def detail(self, response):
        # 外部编号
        url = response.url

        # out_id = url
        out_id = re.findall(r'\d{4}-\d{2}-\d{2}/(.*?)/', url)[0]

        # 标题
        title = response.meta['title']
        # 时间
        push_time = response.meta['tim']
        cover = response.meta['cover']
        # 新闻类型
        new_type = '动点科技'
        # 来源
        source = "动点科技"
        #  摘要
        digest = None
        # 内容
        content = response.xpath('/html/body').extract()
        # 爬取来源
        spider_source = 3

        # print(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     content,
        #     response.url,
        #     spider_source,
        #     cover
        # )

        self.insert_new(
            out_id,
            push_time,
            title,
            new_type,
            source,
            digest,
            content,
            response.url,
            spider_source
        )


        # self.insert_new_1(
        #     out_id,
        #     push_time,
        #     title,
        #     new_type,
        #     source,
        #     digest,
        #     content,
        #     response.url,
        #     spider_source,
        #     cover
        # )
