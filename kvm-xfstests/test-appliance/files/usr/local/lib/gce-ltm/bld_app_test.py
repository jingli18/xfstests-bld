'''
  This is the test app.py function that runs on the build server
  Get the message from ltm server and send the result information back
'''

from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def test_connect():
	print "hello I am here"

@app.route('/sendtobld', methods=['POST'])
def bld_getMessage():
	udata = flask.requests.json # data in unicode
	data = json.dumps(udata, ensure_ascii=False) # get the normal string message
	print "Message recieved from ltm server"
	print data
	print "Now processing the build task"
	time.sleep(5) # pretend to process the task Lol
	ltmurl = data['ltmurl'] + 'sendResult'
	r = requests.post(ltmurl, json=udata)
	print "Sending result message to ltm server"

if __name__ =="__main__":
    app.run(host = '0.0.0.0',port=5000)
