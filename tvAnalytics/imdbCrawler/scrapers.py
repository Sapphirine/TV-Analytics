import subprocess,os,inspect,re

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

import json
import requests

def processSeriesString(seriesName):
	searchString = re.sub("\s\s+", " ", seriesName).strip().encode('ascii','ignore')
	saveString = "_".join(searchString.split(" ")).encode('ascii','ignore').lower()
	return [searchString,saveString]


def uploadBulktoES(filename):
	es = Elasticsearch()
	if os.path.isfile(filename):
		try:
			f = open(filename,'rt')
			data = json.load(f)
			for index,element in enumerate(data):
				episodeInfo = element['episode']
				episodeInfo = episodeInfo.split(',')
				seasonNo = episodeInfo[0].split()
				seasonNo = int(seasonNo[1]) 
				episodeNo = episodeInfo[1].split()
				episodeNo = int(episodeNo[1]) 
				element['seasonNo'] = seasonNo
				element['episodeNo'] = episodeNo
				new_element = dict()
				new_element['_op_type'] = 'create'
				new_element['_index'] = 'tvshows'
				new_element['_type'] = 'episodes'
				new_element['_source'] = element
				data[index] = new_element
			success, _ = bulk(es, data, index='tvshows', raise_on_error=True)
			print('Performed %d actions' % success)
			f.close()
		except Exception:
			print('No DATA')
			f.close()
			os.remove(filename)
			return
		
def uploadSingletoES(filename):
	if os.path.isfile(filename):
		try:
			print filename
			f = open(filename,'rt')
			data = json.load(f)
			ESdata = dict()
			ESdata['showName'] = data['showName']
			ESdata['seasonNo'] = int(data['season'])
			ESdata['episodeNo'] = int(data['episode'])
			ESdata['episode'] = 'Season '+ data['season'] + ', Episode '+data['episode']
			month,day,year = data['airDate'].split('/')
			year = '20'+year
			ESdata['airDate'] = '{}/{}/{}'.format(year,month,day)
			res = requests.post('http://localhost:9200/tvshows/episodes',json.dumps(ESdata))
			print res.json()
			f.close()
		except Exception:
			print('No DATA')
			f.close()
			os.remove(filename)
			return


def scrapeshow(showname):
	#scraper for collecting the show data
	category = 'category="{}"'.format(showname)
	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parentdir = os.path.dirname(currentdir)
	crawlerdir = os.path.join(parentdir,"app","static")
	print crawlerdir
	jsonfile = '{}/{}.json'.format(crawlerdir,processSeriesString(showname)[1])
	subprocess.check_call(['scrapy', 'crawl', 'imdb', '-a', category, '-o', jsonfile, '-t', 'json'])
	uploadBulktoES(jsonfile)
#scraper for validating the next episode
#subprocess.call(['scrapy', 'crawl', 'nextepisode', '-a', 'show=the simpsons', '-o', 'next.json', '-t', 'json',])
#scraper for obtaining the next episode data

def scrapeNewEpisodes():
	#scraper for collecting the show data
	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parentdir = os.path.dirname(currentdir)
	crawlerdir = os.path.join(parentdir,"imdbCrawler")
	print crawlerdir
	subprocess.check_call(['scrapy', 'crawl', 'weekshows','-o','thisweek.json','-t','json'])
#uploadtoES(jsonfile)

def getnewepisodedata(showname):
	category = 'show={}'.format(showname)
	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parentdir = os.path.dirname(currentdir)
	crawlerdir = os.path.join(parentdir,"app","static")
	print crawlerdir
	jsonfile = '{}/{}_newepisode.json'.format(crawlerdir,processSeriesString(showname)[1])
	subprocess.check_call(['scrapy', 'crawl', 'nextepisode', '-a', category])
	uploadSingletoES(jsonfile)
