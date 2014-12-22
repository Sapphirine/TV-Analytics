import subprocess
import beanstalkc

subprocess.call(['beanstalkd','-l','127.0.0.1','-p','14711'])
beanstalk = beanstalkc.Connection(host='localhost', port=14711)
while True:
	job = beanstalk.reserve()
	print job.body
	raw_input("press enter to delete the job")
	job.delete()