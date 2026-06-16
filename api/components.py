from extensions import db
from flask import Blueprint, request, session
from flask_htmx import make_response
from datetime import datetime
from dateutil import tz


components =Blueprint('components',__name__,template_folder="templates")
# METHOD 2: Auto-detect zones:
from_zone = tz.tzutc()
to_zone = tz.tzlocal()
#
#
# This function return an empty string
# DONE: 1
#
# TODO: 0
#
@components.route("/remove",methods=["GET"])
def remove():
    return ''''''

#
#
# This function tests if the endpoints in file work
# DONE: 1
#
# TODO: 0
#
@components.route("/helloComponents", methods=["GET"])
def hello_world():
	return "<p>Hello World, Componennts</p>"

# 
#
# This function returns the html component that displays the room info at the top of the room page.
# DONE:
#
# TODO: 
# redirect if not logged in
@components.route("/session_room/<int:room_id>",methods=["POST","GET"])
def session_room(room_id):
    res=''''''
    if request.method=="GET":
        kicked=db.child("rooms").child("current_rooms").child(str(room_id)).child("kicked").get()
        if kicked.val() and session['uid'] in kicked.val(): return make_response(redirect="/")
        host=db.child("rooms").child("current_rooms").child(str(room_id)).child("host").get().val()
        players =db.child("rooms").child("current_rooms").child(str(room_id)).child("leaderboard").shallow().get().val()
        name=db.child("rooms").child("current_rooms").child(str(room_id)).child("name").get().val()
        state=db.child("rooms").child("current_rooms").child(str(room_id)).child("state").get().val()

        state_label = "Waiting" if state=="w" else ("Finished" if state=="f" else "In Progress")
        state_color = "bg-slate-100 text-slate-600" if state=="w" else ("bg-slate-100 text-slate-600" if state=="f" else "bg-emerald-100 text-emerald-700")
        live_dot = '''<span class="live-dot inline-block w-2 h-2 bg-emerald-500 rounded-full ml-2"></span>''' if state=="s" else ""

        if session['uid']==host:
            res+='''<div class="flex flex-wrap gap-2 mt-4 mb-3">'''
            for player in players:
                if player==host:continue
                res+=f'''<div id=res_{player} class="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-1.5 border border-slate-200">'''
                res+=f'''<span class="text-sm text-slate-700">{db.child("users").child(player).child('name').get().val()}</span>'''
                res+=f'''<button class="text-red-400 hover:text-red-600 hover:bg-red-50 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold transition-colors" hx-post="/kick" hx-target='#res_{player}' uid={player} title="Kick">×</button>'''
                res+='</div>'
            res+='</div>'
            if state=="w": button = '''<button class="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold py-2.5 px-5 rounded-xl transition-colors text-sm shadow-sm" type="button" onclick="startActivity()">▶ Start Activity</button>'''
            else: button = '''<button class="bg-red-500 hover:bg-red-600 text-white font-semibold py-2.5 px-5 rounded-xl transition-colors text-sm shadow-sm" type="button" onclick="stopActivity()">⏹ Stop Activity</button>'''
            res+=f'''
            <div class="flex items-center gap-4 mt-3">
                <div id="stopwatch" class="text-3xl font-mono font-bold text-slate-800 tabular-nums">00:00:00</div>
                {button}
            </div>
            '''
        else:
            res+=f'''<div id="stopwatch" class="text-3xl font-mono font-bold text-slate-800 tabular-nums mt-3">00:00:00</div>'''
        return f'''<div>
            <div class="flex items-center gap-3 mb-1">
                <h1 class="text-2xl font-bold text-slate-800">{name}</h1>
                <span class="text-sm bg-slate-100 text-slate-500 px-2.5 py-1 rounded-lg font-mono">#{room_id}</span>
            </div>
            <div class="flex items-center gap-2 text-sm">
                <span class="text-slate-500">PIN: <strong class="text-slate-700">{room_id}</strong></span>
                <span class="text-slate-300">·</span>
                <span class="inline-flex items-center gap-1.5 {state_color} px-2.5 py-1 rounded-lg text-xs font-semibold">{state_label}{live_dot}</span>
            </div>''' + res + '''</div>'''
 
# 
#
# This function returns the html component that displays the leaderboard info at the right side of the screen.
# DONE:
#
# TODO: 
# redirect if not logged in
@components.route("/leaderboard",methods=["GET"])
def leaderboard():
    room_id=request.referrer.split('/')[-1]
    if not session.get("is_logged_in",False):
        return '''<p class="text-sm text-slate-400 py-2">Log in to see leaderboard</p>'''
    if request.method=="GET":
        leaderboard=db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").get().val()
        if not leaderboard:
            return '''<p class="text-sm text-slate-400 py-2">No players yet</p>'''
        res='''<div class="overflow-x-auto -mx-2"><table class="leaderboard-table w-full text-sm">
            <thead>
                <tr class="border-b border-slate-200">
                <th class="text-left py-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Player</th>
                <th class="text-right py-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">HR</th>
                <th class="text-right py-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Speed</th>
                <th class="text-right py-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Cadence</th>
                <th class="text-right py-2 px-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">Dist</th>
                </tr>
            </thead>
            <tbody>'''
        sorted_players = sorted(leaderboard.items(), key=lambda x: x[1].get("distance",0), reverse=True)
        for i,(uid,data) in enumerate(sorted_players):
            user=db.child("users").child(uid).get().val()
            if not user: continue
            rank_icon = {0:"🥇",1:"🥈",2:"🥉"}.get(i,"")
            res+='''<tr class="border-b border-slate-100">'''
            res+=f'''<td class="py-2.5 px-2 font-medium text-slate-700">{rank_icon} {user["name"]}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-600 tabular-nums">{data.get("avgHeartRate","--")}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-600 tabular-nums">{data.get("avgSpeed","--")}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-600 tabular-nums">{data.get("avgCadence","--")}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right font-semibold text-slate-800 tabular-nums">{round(data.get("distance",0),2)} mi</td>'''
            res+='''</tr>'''
        res+='''</tbody></table></div>'''
        return res
    return '''<p>Whaaaat?</p>'''

@components.route("/deviceDiv",methods=["GET"])
def deviceDiv():
    return '''<div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <div class="flex items-center justify-between mb-3">
                <h2 class="text-lg font-semibold text-slate-800">📡 Devices</h2>
                <button hx-get="/deviceForm" hx-target="#devices" hx-swap="afterbegin"
                    class="bg-slate-100 hover:bg-emerald-50 hover:text-emerald-600 text-slate-600 font-medium py-1.5 px-3 rounded-lg text-sm transition-colors">
                    + Add
                </button>
            </div>
            <div id="devices" class="space-y-2"></div>
        </div>'''

@components.route("/deviceForm",methods=["GET"])
def deviceForm():
    return '''<form class="flex items-center gap-2 p-3 bg-slate-50 rounded-xl border border-slate-200" onSubmit=addDevice(event)>
        <select id="type" name="type" class="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-700 bg-white focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100">
            <option value=0>❤️ Heart Rate</option>
            <option value=1>🚴 Cycling Speed/Cadence</option>
        </select>
        <button class="bg-emerald-500 hover:bg-emerald-600 text-white font-bold w-7 h-7 rounded-lg text-sm transition-colors" type="submit">✓</button>
        <button hx-get="/remove" hx-target="closest form" hx-swap="outerHTML" class="bg-slate-200 hover:bg-red-100 hover:text-red-500 text-slate-500 font-bold w-7 h-7 rounded-lg text-sm transition-colors" type="button">×</button>
    </form>'''

@components.route("/monitor",methods=["GET"])
def monitor():
    return '''
    <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
        <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Live Metrics</h3>
        <div class="grid grid-cols-4 gap-3">
            <div class="bg-slate-50 rounded-xl p-3 text-center">
                <p id="distance" class="text-2xl font-bold text-slate-800 tabular-nums">0.00</p>
                <p class="text-xs text-slate-400 mt-1">miles</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 text-center">
                <p id="speed" class="text-2xl font-bold text-slate-800 tabular-nums">--</p>
                <p class="text-xs text-slate-400 mt-1">mph</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 text-center">
                <p id="cadence" class="text-2xl font-bold text-slate-800 tabular-nums">--</p>
                <p class="text-xs text-slate-400 mt-1">rpm</p>
            </div>
            <div class="bg-slate-50 rounded-xl p-3 text-center">
                <p id="hr" class="text-2xl font-bold text-slate-800 tabular-nums">--</p>
                <p class="text-xs text-slate-400 mt-1">bpm</p>
            </div>
        </div>
    </div>'''

@components.route("/results/<string:room_id>",methods=["GET"])
def results(room_id):
    leaderboard = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").order_by_child("distance").limit_to_first(3).get().val()

    # Podium
    podiums = {0:"🥇", 1:"🥈", 2:"🥉"}
    podium_html='''<div class="space-y-2">'''
    for i,player in enumerate(leaderboard):
        user_name = db.child("users").child(player).child("name").get().val()
        distance = leaderboard[player].get('distance',0)
        podium_html+=f'''<div class="flex items-center justify-between bg-slate-50 rounded-xl px-4 py-3">
            <div class="flex items-center gap-3">
                <span class="text-xl">{podiums.get(i,"")}</span>
                <span class="font-semibold text-slate-800">{user_name}</span>
            </div>
            <span class="font-bold text-emerald-600">{round(distance,2)} mi</span>
        </div>'''
    podium_html+='''</div>'''

    stats = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").child(session['uid']).get().val()
    name = db.child("rooms").child("past_rooms").child(room_id).child("name").get().val()

    statDiv=f''''''
    statDiv+=f'''<div class="bg-slate-50 rounded-xl p-3 text-center"><p class="text-xs text-slate-400 uppercase tracking-wider">❤️ HR</p><p class="text-lg font-bold text-slate-800 mt-1">{stats.get("avgHeartRate","--")}</p></div>'''
    statDiv+=f'''<div class="bg-slate-50 rounded-xl p-3 text-center"><p class="text-xs text-slate-400 uppercase tracking-wider">📏 Distance</p><p class="text-lg font-bold text-slate-800 mt-1">{stats.get("distance","--")}</p></div>'''
    statDiv+=f'''<div class="bg-slate-50 rounded-xl p-3 text-center"><p class="text-xs text-slate-400 uppercase tracking-wider">🔄 Cadence</p><p class="text-lg font-bold text-slate-800 mt-1">{stats.get("avgCadence","--")}</p></div>'''
    statDiv+=f'''<div class="bg-slate-50 rounded-xl p-3 text-center"><p class="text-xs text-slate-400 uppercase tracking-wider">⚡ Speed</p><p class="text-lg font-bold text-slate-800 mt-1">{stats.get("avgSpeed","--")}</p></div>'''

    buttonDiv=f'''<button hx-get="/strava_login" hx-swap="outerHTML"
        class="bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3 px-6 rounded-xl transition-colors shadow-sm">
        📤 Upload to Strava
    </button>'''

    return f'''<div>
        <div class="text-center mb-6">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-amber-100 rounded-2xl mb-3">
                <span class="text-3xl">🏁</span>
            </div>
            <h1 class="text-2xl font-bold text-slate-800">{name}</h1>
            <p class="text-slate-500 text-sm mt-1">Race Complete</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">{statDiv}</div>
        <div class="mb-6">
            <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Podium</h3>
            {podium_html}
        </div>
        <div class="text-center">{buttonDiv}</div>
    </div>'''

@components.route("/history",methods=["GET"])
def history():
    uid = session['uid']
    history = db.child("users").child(uid).child("history").get().val()
    if not history:
        return '''<div class="text-center py-6">
            <p class="text-slate-400 text-sm">No rides yet. Create or join a room to get started!</p>
        </div>'''
    res = '''<div class="space-y-2">'''
    for key in history:
        name = db.child("rooms").child("past_rooms").child(history[key]).child("name").get().val()
        timestamp = db.child("rooms").child("past_rooms").child(history[key]).child("start").get().val()
        if timestamp:
            d = datetime.fromtimestamp(int(timestamp)//1000)
            sd = d.strftime('%b %d, %Y · %I:%M %p')
        else:
            sd = "Unknown date"
        res+=f'''<div onclick="location.href='/history/{history[key]}'" class="flex items-center justify-between bg-slate-50 hover:bg-emerald-50 rounded-xl px-4 py-3 cursor-pointer transition-colors border border-slate-100 hover:border-emerald-200">
            <span class="font-medium text-slate-700">{name}</span>
            <span class="text-sm text-slate-400">{sd}</span>
        </div>'''
    res += '''</div>'''
    return res
