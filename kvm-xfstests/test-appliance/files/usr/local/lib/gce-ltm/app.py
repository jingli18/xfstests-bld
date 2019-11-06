import os
import sys
import base64
import binascii
import logging
import os
import traceback
import flask
import flask_login
from ltm import LTM
from ltm_login import User
from testrunmanager import TestRunManager

logging.basicConfig(
    filename=LTM.server_log_file,
    format='[%(levelname)s:%(asctime)s '
    '%(filename)s:%(lineno)s-%(funcName)s()] %(message)s',
    datefmt='%Y-%m-%d %H:%m:%S', level=logging.DEBUG)

login_manager = flask_login.LoginManager()
app = flask.Flask(__name__, static_url_path='/static')


@app.errorhandler(401)
def unauthorized_error(error):
  return flask.Response('Login required. Use the password in your GS bucket',
                        401,
                        {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.errorhandler(400)
def bad_request_error(error):
  return flask.Response('Bad request', 400, {})

# The secret key is used by Flask as a server-side secret to prevent tampering
# of session cookies (for authentication). Flask requires that the secret be
# set if sessions are used.
# The LTM is not concerned with long user sessions and isn't really
# restarted regularly, so generating the key on initial setup from a regular
# test appliance is fine.
secret_key_path = '/usr/local/lib/gce-ltm/.ltm_secret_key'
if os.path.isfile(secret_key_path):
  with open(secret_key_path, 'r') as f:
    secret_key = f.read()
else:
  with open(secret_key_path, 'w') as f:
    # slice last value off because it's a newline
    secret_key = binascii.b2a_uu(os.urandom(26))[:-1]
    f.write(secret_key)

app.secret_key = secret_key


@login_manager.user_loader
def load_user(user_id):
  return User.get(user_id)

login_manager.init_app(app)


@app.route('/')
def index():
  logging.info('Request received at /, returning index.html')
  return app.send_static_file('index.html')


@app.route('/login', methods=['POST'])
def login():
  """Endpoint for logging in a user session.

  This endpoint expects json data in the request with the key 'password'
  containing the password of the given user. If the password hash matches the
  single user's password hash, the session of this endpoint will be
  authenticated.

  Returns:
    json object {'result': True} on successful login.
    If the request does not contain json data, or if the 'password'
    key is not present, this will instead return a 400 error.
    If the password is incorrect, this will return a 401 error.
  """
  logging.info('Request received at /login')
  json_data = flask.request.json

  if not json_data or 'password' not in json_data:
    # maybe redirect to /
    logging.info('Login failed due to insufficient request content')
    flask.abort(400)

  password = json_data['password']
  user = User.create_user()
  validated = user.validate_password(password)

  if validated:
    flask_login.login_user(user)
    logging.info('Login successful')
  else:
    logging.info('Login failed')
    flask.abort(401)
  return flask.jsonify({'result': True})

User.create_user()


@app.route('/status')
def status():
  if flask_login.current_user.is_authenticated:
    return flask.jsonify({'status': True})
  else:
    return flask.jsonify({'status': False})


@app.route('/logout')
@flask_login.login_required
def logout():
  logging.info('Request received at /logout')
  flask_login.logout_user()
  return flask.jsonify({'result': True})


@app.route('/gce-xfstests', methods=['POST'])
@flask_login.login_required
def gce_xfstests():
  """Endpoint for launching a gce-xfstests test run.

  This endpoint requires that the session is already logged in. If it isn't,
  Flask will automatically respond with a 403 forbidden.

  The endpoint expects json data in the request contents, with at least the key
  'orig_cmdline'. The value should be a base64 encoding of the original command
  line arguments that were passed to gce-xfstests. The endpoint constructs a
  TestRunManager object given this data, gets test run info, and returns it as
  it launches a test run.

  Returns:
    json object with {'status': True|False} depending on whether the test run
    was successfully started. False may indicate a bug in the server, or a
    lack of available quota. When True, the 'info' key will also be available,
    containing basic information about the test run, and the shards that will
    be created for this test run.

    If the json data is not present, or if the 'orig_cmdline' key is not
    present, this will return a 400 error.
  """
  logging.info('Request received at /gce-xfstests')
  json_data = flask.request.json

  if not json_data:
    logging.warning('No json received')
    flask.abort(400)

  logging.info('Received json_data %s', json_data)
  try:
    cmd_in_base64 = json_data['orig_cmdline']
  except KeyError:
    flask.abort(400)

  try:
    opts = json_data['options']
  except KeyError:
    opts = None


  # If the request json has key 'bldsrv' then get the IP of the build server 
  # and send the command message (encoded in base64) to it with POST.
  try:
  	bldsrv_config = json_data['bldsrv']
  	status = os.popen('gcloud compute instances list')
	instance = []
	for line in status.readlines():
    	instance.append(line)
	BLD_SRV_URL = instance[1].split(' ')[-3]
    all_message = {'encodedCMD': cmd_in_base64,
                   'password': 123456}
    r = requests.post(BLD_SRV_URL, data=all_message)
    time.sleep(10)
    call_TestRunManager(cmd_in_base64, opts)
  except KeyError:
  	bldsrv_config = None
  	call_TestRunManager(cmd_in_base64, opts)


def call_TestRunManager(cmd_in_base64, opts)
  try:
    test_run = TestRunManager(base64.decodestring(cmd_in_base64), opts)
    run_info = test_run.get_info()
    test_run.run()
  except:
    logging.error('Did not successfully run test:')
    logging.error(traceback.format_exc())
    return flask.jsonify({'status': False})

  if not run_info or run_info.keys() == 0:
    return flask.jsonify({'status': False})

  return flask.jsonify({'status': True,
                        'info': run_info})

if __name__ == '__main__':
  app.run(host='0.0.0.0')



