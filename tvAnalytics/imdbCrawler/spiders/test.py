from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from imdbCrawler.items import imdbItem, nxt_episode_data
from itertools import izip
import time

#from scrapy.shell import inspect_response
#inspect_response(response)
#print response.url


class MySpider(CrawlSpider):
    name = "imdb"
    
    def __init__(self, category): 
    	super(MySpider, self).__init__(category) 
    	category = category.strip().replace(" ","%20")
    	self.start_urls = ['http://www.imdb.com/search/title?colors=color&languages=en&title=%s&title_type=tv_series' %category] # urls from which the spider will start crawling
    
    def parse(self,response):
        hxs = Selector(response)
        link = "http://www.imdb.com/"+str(hxs.xpath('//tr[@class="even detailed"][1]//a/@href').extract()[0])
        request = Request(link,callback=self.parse_items)
        yield request
    #rules = [Rule(SgmlLinkExtractor(allow=r"imdb.com/title/tt\d+/"), follow=None,callback='parse_items')]
    	
    #def parse_start_url(self, response):
    #    list(self.parse_items(response))
    
    def parse_items(self, response):
        hxs = Selector(response)
        print "came here"
        
        data = imdbItem()
        data["seriesRating"] = hxs.xpath('//span[@itemprop="ratingValue"]/text()').extract()
        print data["seriesRating"]
        seasonLink = hxs.xpath('//*[@id="title-episode-widget"]/div/div[3]/a/@href').extract()
        print seasonLink
        #Directly go to ratings page
        '''
        if not seasonLink==[]:
            #print data["link"]
            url = data["link"][0]+'epdate'
            request = Request(url,callback=self.parse_episode_ratings)
            request.meta['item'] = data
            yield request
        '''    
    
        #follow season links - can get more data as opposed to above method
        if not seasonLink==[]:
            for season in seasonLink:
                link = 'http://www.imdb.com/'+season
                request = Request(link,callback=self.parse_season_links)
                request.meta['item'] = data
                yield request
     

    def parse_season_links(self,response):
        episodeSelector = Selector(response)
        episodeLinks = episodeSelector.xpath('//div[@itemprop="episodes"]//strong/a/@href').extract()

        for episode in episodeLinks:
            link = 'http://www.imdb.com/'+episode
            request = Request(link,callback=self.parse_episode_data)
            request.meta['item'] = response.meta['item']
            yield request

    def parse_episode_data(self,response):
        episodeDataSelector = Selector(response)
        
        dataInitial = response.meta['item']
        data = imdbItem()
        data['link'] = response.url.strip()
        data["seriesRating"] = dataInitial["seriesRating"][0].strip()
        data['showName'] = episodeDataSelector.xpath('//h2[@class="tv_header"]/a/text()').extract()[0].strip()
        data['episode'] = episodeDataSelector.xpath('//h2[@class="tv_header"]//span[@class="nobr"]/text()').extract()[0].strip()
        data['episodeRating'] = episodeDataSelector.xpath('//span[@itemprop="ratingValue"]/text()').extract()[0].strip()
        data['votes'] = serializeToInt(episodeDataSelector.xpath('//span[@itemprop="ratingCount"]/text()').extract()[0].strip())
        data['genre'] = episodeDataSelector.xpath('//span[@itemprop="genre"]/text()').extract()[0].strip()
        data['director'] = episodeDataSelector.xpath('//div[@itemprop="director"]//span[@itemprop="name"]/text()').extract()[0].strip()
        data['airDate'] = process_date(episodeDataSelector.xpath('//div[@id="title-overview-widget"]//h1[@class="header"]//span[@class="nobr"]/text()').extract()[0].strip())
        data['videoLink'] = process_link(data['showName'], data['episode'])
        data['writers'] = episodeDataSelector.xpath('//div[@itemprop="creator"]//span[@itemprop="name"]/text()').extract()
        return data

    #deprecated for now
    def parse_episode_ratings(self,response):
        hxs = Selector(response)
    
        ratingsData = []
        ratingsRawData = hxs.xpath('//td[@align="right"]/text()').extract()
        dataInitial = response.meta['item']
        for episode,rating,votes in grouped(ratingsRawData, 3):
            data = imdbItem()
            data["title"] = dataInitial["title"]
            data["link"] = dataInitial["link"]
            data["seriesRating"] = dataInitial["seriesRating"]            
            data["episode"] = episode.replace(u'\xa0', u'')
            data["episodeRating"] = rating
            data["votes"] = votes
            ratingsData.append(data)
            

        return ratingsData
        
def grouped(iterable, n):
    return izip(*[iter(iterable)]*n)

def serializeToInt(value):
   value = value.partition(',')
   return int(value[0]+value[2])

def process_date(dates):
    c = time.strptime(dates,"(%d %b. %Y)")
    return time.strftime('%Y/%m/%d',c)

def process_link(showName,episode):
    showName = showName.strip().replace(' ','_').lower()
    episode = episode.strip().replace('eason ','').replace('pisode ','').replace(', ','_').lower()
    return 'http://watchseries.lt/episode/'+showName+'_'+episode+'.html'