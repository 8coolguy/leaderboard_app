from flask import Flask, render_template
from flask_cors import CORS
from stravalib import Client
from download_data import get_api_values


app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")
@app.route("/hello", methods=["GET"])
def hello_world():
	return "<p>Hello World</p>" 

@app.route("/strava_login",methods=["GET"])
def strava_login():
	client=Client()
	s,ids=get_api_values()
	authorize_url = client.authorization_url(client_id=ids, redirect_uri='http://127.0.0.1:5000/post_strava_login', scope=["read"])
	
	return f'<a href="{authorize_url}" class="button">Login</a>'

@app.route("/post_strava_login",methods=["GET"])
def post_strava_login(request):
	print(request)
	
	return render_template("index.html")