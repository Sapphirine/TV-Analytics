import subprocess
import beanstalkc

subprocess.Popen(['beanstalkd','-l','127.0.0.1','-p','14711'])
beanstalk = beanstalkc.Connection(host='localhost', port=14711)
for i in xrange(10):
	print "putting job in a queue"
	beanstalk.put('hey! {}'.format(i))