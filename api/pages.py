from flask import Blueprint, redirect,render_template,session

pages= Blueprint('pages', __name__,template_folder='templates')

@pages.route('/pages')
def test():
	return '''<p>Page Test</p>'''

@pages.route("/", methods=["GET"])
def index():
	if not session.get("is_logged_in",False):
		return redirect('login')
	return render_template("index.html")
@pages.route("/room/<int:room_id>",methods=["POST","GET"])
def room(room_id):
	if not session.get("is_logged_in",False):
		return redirect('login')
	return render_template("room.html", room_id=room_id)
@pages.route("/login", methods=["GET"])
def login():
	return render_template("login.html")

@pages.route("/signup", methods=["GET"])
def signup():
	return render_template("signup.html")
@pages.route("/frogotpassword", methods=["GET"])
def frogotpassword():
	return render_template("frogotpassword.html")
