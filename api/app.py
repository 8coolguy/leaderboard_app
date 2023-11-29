from flask import Flask, render_template, request
from flask_cors import CORS
from stravalib import Client
from datetime import datetime,timedelta
from download_data import get_api_values
import time


app = Flask(__name__)
CORS(app)
s,ids=get_api_values()
i=0

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")
@app.route("/hello", methods=["GET"])
def hello_world():
	return "<p>Hello World</p>" 

@app.route("/strava_login",methods=["GET"])
def strava_login():
	client=Client()
	authorize_url = client.authorization_url(client_id=ids, redirect_uri='http://127.0.0.1:5000/post_strava_login', scope=["read","activity:write"])
	
	return f'<a href="{authorize_url}" class="button">Post Activity</a>'

@app.route("/post_strava_login",methods=["GET"])
def post_strava_login():
	global i
	print(i)
	i+=1
	code=request.args.get("code")
	client=Client()	
	token_response = client.exchange_code_for_token(client_id=ids, client_secret=s, code=code)
	
	access_token = token_response['access_token']
	refresh_token = token_response['refresh_token']
	expires_at = token_response['expires_at']
	client.access_token = token_response['access_token']

	try:
		f=open("activity.fit",mode="rb")
		fit_file=f.read()
		activity=client.upload_activity(
			name="Test Activity 3",
			activity_file=fit_file,
			data_type="fit",
			activity_type="Ride"
		)
		f.close()
	except:
		return f'<p>{str(e)}</p>'
	try:
		# if time.time() > expires_at:
		# 	refresh_response = client.refresh_access_token(
		# 		client_id=ids, client_secret=s, refresh_token=refresh_token
		# 	)
		# 	access_token = refresh_response["access_token"]
		# 	refresh_token = refresh_response["refresh_token"]
		# 	expires_at = refresh_response["expires_at"]
		# 	print(refresh_response)
		# # activity.wait(timeout=20)
		return "<p>Success</p>"
	except Exception as e:
		return f'<p>{str(e)}</p>'
	
