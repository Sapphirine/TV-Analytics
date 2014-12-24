import subprocess
import beanstalkc
import addshowclient
import os,sys,inspect,json
print "addshowworker.py"
try:
	import scrapers
except Exception, e:
	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parentdir = os.path.dirname(currentdir)
	crawlerdir = os.path.join(parentdir,"imdbCrawler")
	sys.path.insert(0,crawlerdir)
	import scrapers

scrapers.scrapeNewEpisodes()
print "Done scraping"
#add to database
with open('22December2014-28December2014.json','rt') as f:
	data = json.load(f)
	for show in data:
		print "processing {}".format(show)
		if addshowclient.addshowclient(str(show)):
			print "{} exists ... getting info for next episode".format(show)
		scrapers.getnewepisodedata(str(show))
		print "{} up to date".format(show)

