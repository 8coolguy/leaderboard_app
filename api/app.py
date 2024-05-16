from flask import Flask, request, session, redirect
from flask_cors import CORS
from flask_htmx import HTMX, make_response
from flask_session import Session
from flask_socketio import SocketIO, emit 
import flask_socketio
from stravalib import Client
from download_data import get_api_values
from extensions import auth, db
from pages import pages
from components import components
import urllib.request

MAX_ROOMS = 10
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super sdfsdfhsidfuhsijdfhskdjfskfhksfhkshfksdhfkjecret key'
app.register_blueprint(pages)
app.register_blueprint(components)

CORS(app)
htmx=HTMX(app)
Session(app)
socketio = SocketIO(app,cors_allowed_origins="*")
import events
s,ids=get_api_values()


#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}


@app.route("/hello", methods=["GET"])
def hello_world():
	return "<p>Hello World</p>" 

@app.route("/strava_login",methods=["GET"])
def strava_login():
	room_id=request.referrer.split('/')[-1]
	uid=session['uid']
	
	client=Client()
	authorize_url = client.authorization_url(client_id=ids, redirect_uri=f'http://127.0.0.1:8000/post_strava_login', scope=["read","activity:write"],state=room_id)
	buttonDiv=''''''
	buttonDiv+=f'''<a href="{authorize_url}" class="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" >You Sure?</a>'''
	return buttonDiv

def getFitFile(room_id,uid):
	urllib.request.urlretrieve(f'https://leaderboard-encoder.azurewebsites.net/weatherforecast/{room_id}/{uid}', f'{room_id}_{uid}.fit')

@app.route("/post_strava_login",methods=["GET"])
def post_strava_login():
	
	code = request.args.get("code")
	room_id = request.args.get("state")
	uid = session['uid']
	name = db.child("rooms").child("past_rooms").child(room_id).child("name").get().val()
	try:
		getFitFile(room_id,uid)
	
	
		client=Client()	
		token_response = client.exchange_code_for_token(client_id=ids, client_secret=s, code=code)
		
		access_token = token_response['access_token']
		refresh_token = token_response['refresh_token']
		expires_at = token_response['expires_at']
		client.access_token = token_response['access_token']

	
		f=open( f'{room_id}_{uid}.fit',mode="rb")
		fit_file=f.read()
		activity=client.upload_activity(
			name=name,
			activity_file=fit_file,
			data_type="fit",
			activity_type="Ride"
		)
		print(activity.status)
		f.close()
		return redirect("/")
	except Exception as e:
		return f'<p>{str(e)}</p>'
		
@app.route("/firebase_login",methods=["POST","GET"])
def firebase_login():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		password=result["pass"]
		try:
			#Try signing in the user with the given information
			user = auth.sign_in_with_email_and_password(email, password)
			
			#insert the user information into the session
			session["is_logged_in"] = True
			session["email"] = user["email"]
			session["uid"] = user["localId"]
			
			#Get the name of the user
			session["name"] = user["displayName"] or email
			db.child("users").child(session["uid"]).update({"name":session["name"]})
			return redirect("/")
		except Exception as e:
			return f'<p>{str(e)}</p>'
	else:
		return "<p>GET</p>"
@app.route("/firebase_register",methods=["POST","GET"])
def firebase_register():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		password=result["pass"]
		password2=result["pass2"]
		if password!=password2: return "uh oh"
		try:
			#Create User
			user = auth.create_user_with_email_and_password(email, password)
			auth.send_email_verification(user['idToken'])
			return "<p>Success Login</p>"	
		except Exception as e:
			return f'<p>{str(e)}</p>'
	else:
		return "<p>GET</p>"
@app.route("/firebase_frogot_password",methods=["POST","GET"])
def firebase_frogot_password():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		try:
			#send recovery email
			auth.send_password_reset_email(email)
			return "<p>Success Login</p>"	
		except Exception as e:
			return f'<p>{str(e)}</p>'
	else:
		return "<p>GET</p>"
@app.route("/session_user",methods=["POST","GET"])
def session_user():
	if request.method =="GET":
		if session.get("is_logged_in",False):
			return f'''<div class="flex justify-center items-center"><h1 class="text-xl font-bold ">Welcome</h1> <h1 class="text-l text-green-600 pl-3">{session.get("name","Arnav")}</h1></div>'''
					
@app.route("/logout",methods=["POST","GET"])
def logout():
	if request.method =="GET":
		if session.get("is_logged_in",False):
			auth.current_user=None
			session["is_logged_in"]=False
			return make_response(
				redirect="/"
			)
	return make_response(redirect="/")

@app.route("/create_room",methods=["POST","GET"])
def create_room():
	if request.method =="POST" and session.get("is_logged_in",False):
		result=request.form
		name=result["name"]
		
		data={"name":name,"players":{},"kicked":{},"host":session['uid'],"type":"private"}
		
		room_id=-1
		rooms=db.child("rooms").child("current_rooms").shallow().get().val()

		for i in range(1,MAX_ROOMS):
			if rooms and str(i) in rooms:
				continue
			res=db.child("rooms").child("past_rooms").push(data)
			data["id"]=res["name"]
			data["state"]="w"
			res=db.child("rooms").child("current_rooms").child(str(i)).set(data)
			room_id=i
			break
		if room_id==-1:
			return redirect('/') #1000 rooms filled need to figure out what max bandwidth would be.
		return redirect(f'''/room/{room_id}''')


@app.route("/join_room",methods=["POST","GET"])
def join_room():
	if request.method =="POST" and session.get("is_logged_in",False):
		result=request.form
		room_id=result["room_id"]
		if not room_id.isnumeric() or not 0<int(room_id) <100: return redirect(f'''/''')
		if not str(room_id) in db.child("rooms").child("current_rooms").shallow().get().val(): return redirect(f'''/''')
		player=db.child("rooms").child("current_rooms").child(str(room_id)).child("leaderboard").child(session['uid']).update({"name":session["name"]})
		return redirect(f'''/room/{room_id}''')
@app.route("/kick",methods=["POST","GET"])
def kick():
	if request.method =="POST" and session.get("is_logged_in",False):
		uid=request.headers['Hx-Target'][4:]
		room_id=request.referrer.split('/')[-1]
		#notify that you can kick host
		if uid==db.child("rooms").child("current_rooms").child(room_id).child("host").get().val():
			return make_response(redirect=request.referrer)
		
		player=db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(uid).remove()
		player=db.child("rooms").child("current_rooms").child(str(room_id)).child("kicked").update({str(uid):"1"})
		return '''<p></p>'''


