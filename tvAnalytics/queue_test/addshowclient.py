import subprocess
import beanstalkc
import requests


def addshowclient(showname):
	#check if showname exists in database
	print showname
	r = requests.get("http://localhost:9200/tvshows/_count?q=showName:"+showname)
	r = r.json()
	exists = True if r['count'] > 0 else False
	if exists:
		print "Exists"
		return True
	else:
		subprocess.Popen(['beanstalkd','-l','127.0.0.1','-p','14711'])
		beanstalk = beanstalkc.Connection(host='localhost', port=14711)
		beanstalk.use('addshow')
		beanstalk.put(showname)
		return False

