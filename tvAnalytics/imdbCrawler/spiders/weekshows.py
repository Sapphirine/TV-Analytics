from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
import os, json

class WeekShows(CrawlSpider):
	name = "weekshows"
	def __init__(self):
		super(WeekShows, self).__init__()
		self.start_urls = ["http://tvshowcalendar.com/"]	

	def parse(self,response):
		hxs = Selector(response)

		week = "".join(hxs.xpath('//h2[@class="darkblue"]/span/text()').extract()[0].split())
		if os.path.isfile("{}.json".format(week)):
			return
		else:
			data = list(set(hxs.xpath('//td[@class="show"]/a/text()').extract()))
			data = json.dumps(data)
			with open("{}.json".format(week),'wt') as f:
				f.write(data)
