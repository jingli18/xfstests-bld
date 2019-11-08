import os
import requests
from time import time

try:
  instance = {'bldsrvurl': 'http://35.192.187.93:5000/',
              'ltmsrvurl': 'http://35.225.191.203:5000/',
              'cmd': 'xfs-tests bld commit master ltm smoke'}
  url = str(instance['ltmsrvurl'])+'user'

  r = requests.post(url, json=instance)

  print "The build server's URL has been sended to the LTM server"

except KeyError:
	bldsrv_config = None
	call_TestRunManager(cmd_in_base64, opts)
