'''
  This function will get the ip address of all instances that running on the GCE
  and send the urls to the build server
  Need to connect with the bash script to get the command message
'''

import os
import requests
from time import time

ori_cmd = 'gce-xfstests bld commit master ltm smoke' # this cmd should be sent by a script
status = os.popen('gcloud compute instances list')
instance = {'oricmd': ori_cmd}
instance_name, instance_url = [], []
for line in status.readlines():
  instance_name.append(line.split(' ')[0])
  instance_url.append(line.split(' ')[-3])
for i in range(1, len(instance_name)):
  instance[instance_name[i]] = instance_url[i]
bldsrv_url = 'http://' + instance['instance-1']
ltm_url = 'http://' + instance['instance-2']
requestUrl = ltm_url + '/sendtobld'
r = requests.post(requestUrl, json=instance)

print "The build server's URL has been sended to the LTM server"

