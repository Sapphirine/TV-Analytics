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
subprocess.Popen(['beanstalkd','-l','127.0.0.1','-p','14711'])
print "About to connect to stuff"
beanstalk = beanstalkc.Connection(host='localhost', port=14711)
print "About to watch stuff"
beanstalk.watch('addshow')
print "About to enter infinite loop"
while True:
	print "Waiting for a job"
	job = beanstalk.reserve()
	print job.body
	print "About to run the scraper"
	scrapers.scrapeshow(job.body)
	print "Done scraping"
	#add to database
	job.delete()
	print "Job Done"
