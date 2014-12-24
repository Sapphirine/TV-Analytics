import subprocess
import beanstalkc
import os,sys,inspect
print "addshowworker.py"
try:
	import scrapers
except Exception, e:
	currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	parentdir = os.path.dirname(currentdir)
	crawlerdir = os.path.join(parentdir,"imdbCrawler")
	sys.path.insert(0,crawlerdir)
	import scrapers
print "done trying to do complicated stuff"
print "About to run the scraper"
scrapers.scrapeNewEpisodes()
print "Done scraping"
#add to database
