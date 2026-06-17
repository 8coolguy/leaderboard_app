from flask import Flask, request, session, redirect, url_for, render_template, send_file
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
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import os
import tempfile

MAX_ROOMS = 10

# ── Firebase error → human-readable messages ──────────────────────────────
FIREBASE_ERRORS = {
    "INVALID_LOGIN_CREDENTIALS": ("Invalid credentials", "The email or password you entered is incorrect."),
    "INVALID_EMAIL": ("Invalid email", "Please enter a valid email address."),
    "EMAIL_NOT_FOUND": ("Account not found", "No account exists with this email address. Sign up first."),
    "INVALID_PASSWORD": ("Wrong password", "The password you entered is incorrect. Try again or reset it."),
    "USER_DISABLED": ("Account disabled", "This account has been disabled. Contact support for help."),
    "EMAIL_EXISTS": ("Email already in use", "An account with this email already exists. Try logging in instead."),
    "WEAK_PASSWORD": ("Weak password", "Password should be at least 6 characters long."),
    "TOO_MANY_ATTEMPTS": ("Too many attempts", "Too many tries. Please wait a moment and try again."),
    "MISSING_EMAIL": ("Missing email", "Please provide an email address."),
    "MISSING_PASSWORD": ("Missing password", "Please provide a password."),
    "USER_NOT_FOUND": ("Account not found", "No account found with this email address."),
}

def firebase_error(e):
    """Parse a Firebase exception into (title, message) tuple."""
    msg = str(e)
    # Firebase errors come as JSON, try to extract the message
    import json
    try:
        err = json.loads(msg.replace("'", '"'))
        code = err.get("error", {}).get("message", "") if isinstance(err, dict) else ""
    except (json.JSONDecodeError, AttributeError):
        code = ""
    for key, (title, detail) in FIREBASE_ERRORS.items():
        if key in msg or key in code:
            return title, detail
    # Fallback: try to clean up the raw error
    clean = msg.replace("{", "").replace("}", "").replace("'", "")
    if len(clean) > 120:
        clean = clean[:120] + "…"
    return "Something went wrong", clean if clean else "An unexpected error occurred. Please try again."

def render_error(title, message, back_url=None, back_label=None):
    """Render the error page template."""
    return render_template(
        "partials/error_page.html",
        error_title=title,
        error=message,
        back_url=back_url or "/login",
        back_label=back_label or "Back to Sign In"
    )
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
	authorize_url = client.authorization_url(client_id=ids, redirect_uri=url_for('post_strava_login',_external=True), scope=["read","activity:write"],state=room_id)
	buttonDiv=''''''
	buttonDiv+=f'''<a href="{authorize_url}" class="bg-orange-500 hover:bg-orange-600 text-white text-sm font-medium py-2.5 px-5 rounded-lg transition-colors inline-block" >Upload to Strava</a>'''
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
		return render_error("Strava upload failed", "Could not upload your ride to Strava. The encoder service may be unavailable. Your ride data is saved and you can try again later.\n\nError: " + str(e)[:200], back_url="/", back_label="Back to Dashboard")
		
@app.route("/firebase_login",methods=["POST","GET"])
def firebase_login():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		password=result["pass"]
		if not email or not password:
			return render_error("Missing fields", "Please enter both your email and password.")
		try:
			user = auth.sign_in_with_email_and_password(email, password)
			session["is_logged_in"] = True
			session["email"] = user["email"]
			session["uid"] = user["localId"]
			session["name"] = user["displayName"] or email
			db.child("users").child(session["uid"]).update({"name":session["name"]})
			return redirect("/")
		except Exception as e:
			title, msg = firebase_error(e)
			return render_error(title, msg, back_url="/login", back_label="Try Again")
	else:
		return "<p>GET</p>"
@app.route("/firebase_register",methods=["POST","GET"])
def firebase_register():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		password=result["pass"]
		password2=result["pass2"]
		if not email or not password:
			return render_error("Missing fields", "Please fill in all required fields.", back_url="/signup", back_label="Try Again")
		if password!=password2:
			return render_error("Passwords don't match", "The two passwords you entered are different. Please try again.", back_url="/signup", back_label="Try Again")
		try:
			user = auth.create_user_with_email_and_password(email, password)
			auth.send_email_verification(user['idToken'])
			return render_template("partials/error_page.html",
				error_title="Check your email",
				error="We sent a verification link to " + email + ". Please verify your account, then sign in.",
				back_url="/login",
				back_label="Go to Sign In")
		except Exception as e:
			title, msg = firebase_error(e)
			return render_error(title, msg, back_url="/signup", back_label="Try Again")
	else:
		return "<p>GET</p>"
@app.route("/firebase_forgot_password",methods=["POST","GET"])
def firebase_forgot_password():
	if request.method =="POST":
		result=request.form
		email=result["email"]
		if not email:
			return render_error("Missing email", "Please enter your email address.", back_url="/forgotpassword", back_label="Try Again")
		try:
			auth.send_password_reset_email(email)
			return render_template("partials/error_page.html",
				error_title="Email sent",
				error="If an account exists for " + email + ", you will receive a password reset email shortly.",
				back_url="/login",
				back_label="Back to Sign In")
		except Exception as e:
			title, msg = firebase_error(e)
			return render_error(title, msg, back_url="/forgotpassword", back_label="Try Again")
	else:
		return "<p>GET</p>"
@app.route("/session_user",methods=["POST","GET"])
def session_user():
	if request.method =="GET":
		if session.get("is_logged_in",False):
			return f'''<div><h1 class="text-xl font-semibold text-slate-900">Welcome back, {session.get("name","Rider")}</h1></div>'''
					
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
@app.route("/download/<string:room_id>", methods=["GET"])
def download_fit(room_id):
	if not session.get("is_logged_in", False):
		return redirect("/login")

	uid = session['uid']
	name = db.child("rooms").child("past_rooms").child(room_id).child("name").get().val() or "ride"

	# 1. Try the encoder for a proper FIT file
	try:
		getFitFile(room_id, uid)
		fit_path = f'{room_id}_{uid}.fit'
		if os.path.exists(fit_path) and os.path.getsize(fit_path) > 0:
			return send_file(
				fit_path,
				as_attachment=True,
				download_name=f'{name}_{room_id}.fit',
				mimetype='application/octet-stream'
			)
	except Exception:
		pass

	# 2. Fallback: generate GPX from stored session data
	try:
		gpx_path = _generate_gpx(room_id, uid, name)
		if gpx_path:
			return send_file(
				gpx_path,
				as_attachment=True,
				download_name=f'{name}_{room_id}.gpx',
				mimetype='application/gpx+xml'
			)
	except Exception as e:
		print(f"GPX generation failed: {e}")

	return render_error(
		"Download failed",
		"Could not generate a ride file. The encoder service is unavailable and there is no saved session data to export.",
		back_url=f"/history/{room_id}",
		back_label="Back to results"
	)


def _generate_gpx(room_id, uid, name):
	"""Generate a GPX file from stored Firebase ride data."""
	safe_name = "".join(c for c in name if c.isalnum() or c in ' _-')[:50]

	# Pull player data points: rooms/past_rooms/{room_id}/players/{uid}/
	player_data = db.child("rooms").child("past_rooms").child(room_id).child("players").child(uid).get().val()
	if not player_data:
		return None

	# Sort by timestamp (keys are epoch seconds)
	points = []
	for ts, values in sorted(player_data.items(), key=lambda x: int(x[0])):
		try:
			t = datetime.fromtimestamp(int(ts), tz=timezone.utc)
		except (ValueError, OSError):
			continue
		hr = values.get("heartRate")
		cad = values.get("cadence")
		spd = values.get("speed")
		dist = values.get("distance")
		points.append({"time": t, "hr": hr, "cad": cad, "speed": spd, "dist": dist})

	if len(points) < 2:
		return None

	# Build GPX XML
	gpx = ET.Element("gpx", {
		"version": "1.1",
		"creator": "VirtualCyclingLeaderboard",
		"xmlns": "http://www.topografix.com/GPX/1/1",
		"xmlns:gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
	})

	trk = ET.SubElement(gpx, "trk")
	ET.SubElement(trk, "name").text = name
	ET.SubElement(trk, "type").text = "virtual_ride"
	trkseg = ET.SubElement(trk, "trkseg")

	for pt in points:
		trkpt = ET.SubElement(trkseg, "trkpt", {"lat": "0", "lon": "0"})
		ET.SubElement(trkpt, "time").text = pt["time"].strftime("%Y-%m-%dT%H:%M:%SZ")
		if pt["dist"] is not None:
			ET.SubElement(trkpt, "distance").text = str(round(pt["dist"] * 1609.34, 1))

		extensions = ET.SubElement(trkpt, "extensions")
		tpx = ET.SubElement(extensions, "gpxtpx:TrackPointExtension")
		if pt["hr"] is not None:
			ET.SubElement(tpx, "gpxtpx:hr").text = str(int(pt["hr"]))
		if pt["cad"] is not None:
			ET.SubElement(tpx, "gpxtpx:cad").text = str(int(pt["cad"]))

	tree = ET.ElementTree(gpx)
	ET.indent(tree, space="  ")

	tmp = tempfile.NamedTemporaryFile(mode="w+b", suffix=".gpx", delete=False)
	tree.write(tmp, encoding="utf-8", xml_declaration=True)
	tmp.close()
	return tmp.name

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


