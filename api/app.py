from flask import Flask, render_template, request
from flask_cors import CORS
from stravalib import Client
from datetime import datetime,timedelta
from download_data import get_api_values


app = Flask(__name__)
CORS(app)
s,ids=get_api_values()

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
	
	return f'<a href="{authorize_url}" class="button">Login</a>'

@app.route("/post_strava_login",methods=["GET"])
def post_strava_login():
	code=request.args.get("code")
	client=Client()	
	token_response = client.exchange_code_for_token(client_id=ids, client_secret=s, code=code)
	
	access_token = token_response['access_token']
	refresh_token = token_response['refresh_token']
	expires_at = token_response['expires_at']
	client.access_token = token_response['access_token']
	activity=client.create_activity(
		name="fkjsdfbkjs",
		start_date_local=datetime.now(),
		elapsed_time=timedelta(minutes=5),
		activity_type="Ride"
	)
	return render_template("index.html")
