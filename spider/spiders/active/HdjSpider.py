from scrapy import Request
from spider.spiders.active.ActiveSpider import ActiveSpider
"""
活动家  ===   it、医疗科学、金融财经
"""


class HdjSpider(ActiveSpider):
    #  爬虫的名字 <爬虫启动时使用  scrapy crawl xiniu>
    name = "hdj_active"
    # 爬取的范围，防治爬虫爬到别的网站
    allowed_domains = ["huodongjia.com"]
    #  开始爬取的地址  按照行业分类来爬取
    start_urls = 'https://www.huodongjia.com/{active_type}/page-{num}/'

    base_url = "https://www.huodongjia.com"

    active_types = [
        {"name": "it", "value": "it"},
        {"name": "医疗医学", "value": "medical"},
        {"name": "金融财经", "value": "finance"}
    ]

    def __init__(self, *a, **kw):
        super(HdjSpider, self).__init__(*a, **kw)

    def start_requests(self):
        for active_type in self.active_types:
            yield Request(
                     self.start_urls.format(active_type=active_type.get("value"), num=1),
                     meta=active_type,
                     dont_filter=True
            )

    def parse(self, response):
        data_list = response.xpath('//div[@class="all_events"]/div[@class="eventList"]')
        if data_list is not None:
            for data in data_list:
                title = data.xpath('./div/h3/a/text()').extract_first()
                link = data.xpath('./div/h3/a/@href').extract_first()
                link = self.base_url+link
                times = data.xpath('./div/p[@class="address"][1]/text()').get().strip()
                place = data.xpath('./div/p[@class="address"][1]/a/text()').extract_first()
                classify = response.meta['name']
                source = "活动家"
                tags_data = data.xpath('./div/p[@class="meeting_tags"]//a//text()').extract()
                tags = ""
                if tags_data is not None and len(tags_data) != 0:
                    for i, tag in enumerate(tags_data):
                        tags += tag
                        if i != len(tags_data) - 1:
                            tags = tags + "、"
                # # 插入sql
                # pojo = self.fetchone(
                #     "SELECT 1 FROM `financial_activities` WHERE `link`='%s' AND `source`='%s' " % (
                #     link, source)
                # )
                # if pojo is None:
                #     self.insert_new(
                #         title,
                #         times,
                #         place,
                #         tags,
                #         classify,
                #         link,
                #         source
                #     )

                # 详情页
                yield Request(
                    link,
                    meta={
                        "title": title,
                        "place": place,
                        "tags": tags,
                        "classify": classify,
                        "link": link,
                        "new_time": times,
                        "source": source
                    },
                    callback=self.detail
                )
            next_url = response.xpath('//div[@class="pagination"]/ul/li[last()]/a/@href').extract_first()
            if next_url is not None:
                pageNo = str(next_url).split("-")[1][0:1]
                # 只抓取前5页的数据
                if int(pageNo) <= 5:
                    next_url = self.base_url+next_url
                    # yield Request(next_url, callback=self.parse)
                    yield Request(next_url, dont_filter=True, meta=response.meta, callback=self.parse)
                else:
                    return

            else:
                return
        else:
            return

    def detail(self, response):
        title = response.meta['title']
        place = response.meta['place']
        tags = response.meta['tags']
        classify = response.meta['classify']
        link = response.meta['link']
        source = response.meta['source']
        times = response.meta['new_time']
        sponsors = response.xpath('//*[@id="meeting_1"]/div/div[2]/span//a//text()').extract()
        sponsor = ""
        if sponsors is not None and len(sponsors) != 0:
            for i, tag in enumerate(sponsors):
                sponsor += tag
                if i != len(sponsors) - 1:
                    sponsor = sponsor + "、"

        self.insert_new(
            title,
            times,
            place,
            tags,
            classify,
            link,
            source,
            sponsor
        )


