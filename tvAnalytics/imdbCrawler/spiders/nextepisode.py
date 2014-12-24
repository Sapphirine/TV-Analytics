from scrapy.contrib.spiders import CrawlSpider

from imdbCrawler.items import nextepisodeItem
from scrapy.selector import Selector
import re
import json
import os,inspect

class NextEpisodeSpider(CrawlSpider):
	name = "nextepisode"
	def __init__(self,show):
		super(NextEpisodeSpider, self).__init__(show)
		self.showoriginal = show
		self.show = self.preprocess(show)
		self.start_urls = ["http://www.tv.com/shows/{}/".format(self.show)]

	def preprocess(self,show):
		show = show.strip().replace(" ","-").lower()
		return show
		
	def parse(self,response):
		hxs = Selector(response)
		data = nextepisodeItem()
		nextepisode = hxs.xpath('//tr[@class="episode next"][1]/td[@class="title"]/span/text()').extract()
		if len(nextepisode)>0:
			data['exists'] = True
			data['showName'] = self.showoriginal
			data['episodeName'] = str(hxs.xpath('//tr[@class="episode next"][1]/td[@class="title"]/a/span[@itemprop="name"]/text()').extract()[0])
			b = hxs.xpath('//tr[@class="episode next"][1]/td[@class="date"]/a/text()').extract()[0].strip()
			data['airDate'] = b.split(' ')[1]
			a = hxs.xpath('//tr[@class="episode next"][1]/td[@class="nums"]/a/text()').extract()[0].strip()
			data['season'] = re.search(r'\d+',"".join(a.split()).split(':')[0]).group()
			data['episode'] =  re.search(r'\d+',hxs.xpath('//tr[@class="episode next"][1]/td[@class="nums"]/a/span/text()').extract()[0]).group()
			
			currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
			parentdir = os.path.dirname(os.path.dirname(currentdir))
			crawlerdir = os.path.join(parentdir,"app","static")
			jsonfile = '{}/{}_newepisode.json'.format(crawlerdir,self.show)
			print '\n\n'
			print crawlerdir
			print data
			print '\n\n'
			with open(jsonfile.replace('-','_'),'wt') as f:
				json.dump(dict(data),f)
		else:
			data['exists'] = False

		return data
	

