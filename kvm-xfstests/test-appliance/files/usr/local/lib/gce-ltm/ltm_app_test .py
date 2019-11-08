'''
  This is the test app.py function that runs on the ltm server
  Get the message from user and communicate with the build server
'''

from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def test_connect():
	print "hello I am here"

@app.route('/sendtoltm', methods=['POST'])
def ltm_getMessage():
	udata = flask.requests.json # data in unicode
	data = json.dumps(udata, ensure_ascii=False) # get the normal string message
	print "Message recieved from user"
	print data
	bldurl = data['bldsrvurl'] + 'sendtobld'
	r = requests.post(bldurl, json=udata)
	print "Sending message to build server"

@app.rout('/sendResult', methods=['POST'])
def ltm_getResuld():
	udata = flask.requests.json # data in unicode
	data = json.dumps(udata, ensure_ascii=False) # get the normal string message
	print "Message recieved from build server"
	print data

if __name__ =="__main__":
    app.run(host = '0.0.0.0',port=5000)
