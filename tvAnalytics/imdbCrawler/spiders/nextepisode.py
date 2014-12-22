from scrapy.contrib.spiders import CrawlSpider

from imdbCrawler.items import nextepisodeItem
from scrapy.selector import Selector
import re


class NextEpisodeSpider(CrawlSpider):
	name = "nextepisode"
	def __init__(self,show):
		super(NextEpisodeSpider, self).__init__(show)
		show = self.preprocess(show)
		self.start_urls = ["http://www.tv.com/shows/{}/".format(show)]

	def preprocess(self,show):
		show = show.strip().replace(" ","-").lower()
		return show
	def parse(self,response):
		hxs = Selector(response)
		data = nextepisodeItem()
		nextepisode = hxs.xpath('//tr[@class="episode"][1]/td[@class="title"]/span/text()').extract()
		if len(nextepisode)>0:
			data['exists'] = True
			data['airDate'] = hxs.xpath('//tr[@class="episode"][1]/td[@class="date"]/a/text()').extract()[0].strip()
			a = hxs.xpath('//tr[@class="episode"][1]/td[@class="nums"]/a/text()').extract()[0].strip()
			data['season'] = re.search(r'\d+',"".join(a.split()).split(':')[0]).group()
			data['episode'] =  re.search(r'\d+',hxs.xpath('//tr[@class="episode"][1]/td[@class="nums"]/a/span/text()').extract()[0]).group()

		else:
			data['exists'] = False

		return data
	

