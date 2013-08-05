#!/usr/bin/env python

import twitter
import threading
import pynotify
import os
import sys
import time
import syslog

CHECK_INTERVAL = 60

class EmptyEnvironmentVariable(Exception):
	pass

def raise_if_empty(variable_name, variable):
	if variable == None or variable == '':
		raise EmptyEnvironmentVariable('{0} environment variable cannot be empty\n'.format(
				variable_name))

def notify_recent_tweet():

	if not pynotify.init('tweet-gnome-notify'):
		syslog.syslog("Couldn't initialize notify -- exiting\n")
		sys.exit(1)

	rc_path = os.path.join(os.getenv('HOME'),'.tweet-gnome-notify')
	if not os.path.exists(rc_path):
		os.makedirs(rc_path)

	consumer_key = os.getenv('CONSUMER_KEY')
	raise_if_empty('CONSUMER_KEY', consumer_key)
	consumer_secret = os.getenv('CONSUMER_SECRET')
	raise_if_empty('CONSUMER_SECRET', consumer_secret)
	access_token_key = os.getenv('ACCESS_TOKEN_KEY')
	raise_if_empty('ACCESS_TOKEN_KEY', access_token_key)
	access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
	raise_if_empty('ACCESS_TOKEN_SECRET', access_token_secret)

	api = twitter.Api(consumer_key=consumer_key,
					  consumer_secret=consumer_secret,
					  access_token_key=access_token_key,
					  access_token_secret=access_token_secret)

	statuses = api.GetHomeTimeline(count=1)
	if len(statuses) >= 1:
		status = statuses[0].AsDict()

		last_tweet_file = os.path.join(rc_path,'last_tweet')
		last_tweet = ''
		if os.path.exists(last_tweet_file):
			f = open(last_tweet_file)
			last_tweet = f.readline()
			f.close()

		if status['text'] != last_tweet:
			notice = pynotify.Notification(status['user']['name'],status['text'])
			notice.show()
			f = open(last_tweet_file,'w+')
			f.write(status['text'])
			f.close()

if __name__ == '__main__':
	syslog.syslog("Starting tweet-gnome-notify\n")
	while True:
		try:
			notify_recent_tweet()
		except Exception:
			syslog.syslog("Uncaught exception\n")
			syslog.syslog("{0}\n".format(Exception))
		time.sleep(CHECK_INTERVAL)


