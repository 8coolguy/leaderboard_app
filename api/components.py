from extensions import db
from flask import Blueprint, request, session
from flask_htmx import make_response
from datetime import datetime
from dateutil import tz


components =Blueprint('components',__name__,template_folder="templates")
from_zone = tz.tzutc()
to_zone = tz.tzlocal()

@components.route("/remove",methods=["GET"])
def remove():
    return ''''''

@components.route("/helloComponents", methods=["GET"])
def hello_world():
	return "<p>Hello World, Components</p>"

@components.route("/session_room/<int:room_id>",methods=["POST","GET"])
def session_room(room_id):
    res=''''''
    if request.method=="GET":
        kicked=db.child("rooms").child("current_rooms").child(str(room_id)).child("kicked").get()
        if kicked.val() and session['uid'] in kicked.val(): return make_response(redirect="/")
        host=db.child("rooms").child("current_rooms").child(str(room_id)).child("host").get().val()
        players =db.child("rooms").child("current_rooms").child(str(room_id)).child("leaderboard").shallow().get().val()
        if not players:
            players = []
        name=db.child("rooms").child("current_rooms").child(str(room_id)).child("name").get().val()
        state=db.child("rooms").child("current_rooms").child(str(room_id)).child("state").get().val()

        state_label = "Waiting" if state=="w" else ("Finished" if state=="f" else "In Progress")
        state_color = "bg-slate-100 text-slate-500" if state!="s" else "bg-emerald-50 text-emerald-700"
        live_dot = '''<span class="live-dot inline-block w-1.5 h-1.5 bg-emerald-500 rounded-full ml-1.5"></span>''' if state=="s" else ""

        if session['uid']==host:
            res+='''<div class="flex flex-wrap gap-2 mt-4 mb-3">'''
            for player in players:
                if player==host:continue
                res+=f'''<div id=res_{player} class="flex items-center gap-2 bg-slate-50 rounded-lg px-3 py-1.5 ring-1 ring-slate-200">'''
                res+=f'''<span class="text-xs text-slate-600">{db.child("users").child(player).child('name').get().val()}</span>'''
                res+=f'''<button class="text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-full w-5 h-5 flex items-center justify-center text-xs transition-colors" hx-post="/kick" hx-target='#res_{player}' uid={player} title="Remove player">&times;</button>'''
                res+='</div>'
            res+='</div>'
            if state=="w": button = '''<button class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2.5 px-5 rounded-lg transition-colors" type="button" onclick="startActivity()">Start activity</button>'''
            else: button = '''<button class="bg-red-500 hover:bg-red-600 text-white text-sm font-medium py-2.5 px-5 rounded-lg transition-colors" type="button" onclick="stopActivity()">Stop activity</button>'''
            res+=f'''
            <div class="flex items-center gap-4 mt-3">
                <div id="stopwatch" class="text-3xl font-mono font-semibold text-slate-800 tabular-nums tracking-tight">00:00:00</div>
                {button}
            </div>
            '''
        else:
            res+=f'''<div id="stopwatch" class="text-3xl font-mono font-semibold text-slate-800 tabular-nums tracking-tight mt-3">00:00:00</div>'''
        return f'''<div>
            <div class="flex items-center gap-3 mb-1">
                <h1 class="text-xl font-semibold text-slate-900">{name}</h1>
                <span class="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-md font-mono">#{room_id}</span>
            </div>
            <div class="flex items-center gap-2 text-xs">
                <span class="text-slate-400">PIN <span class="text-slate-600 font-medium">{room_id}</span></span>
                <span class="text-slate-200">&middot;</span>
                <span class="inline-flex items-center gap-1 {state_color} px-2 py-0.5 rounded-md font-medium">{state_label}{live_dot}</span>
            </div>''' + res + '''</div>'''

@components.route("/leaderboard",methods=["GET"])
def leaderboard():
    room_id=request.referrer.split('/')[-1]
    if not session.get("is_logged_in",False):
        return '''<p class="text-xs text-slate-400 py-2">Sign in to see the leaderboard</p>'''
    if request.method=="GET":
        leaderboard=db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").get().val()
        if not leaderboard:
            return '''<p class="text-xs text-slate-400 py-2">No players yet</p>'''
        res='''<table class="leaderboard-table w-full text-xs">
            <thead>
                <tr class="border-b border-slate-100">
                <th class="text-left py-2 pr-2 font-medium text-slate-400">Name</th>
                <th class="text-right py-2 px-2 font-medium text-slate-400">HR</th>
                <th class="text-right py-2 px-2 font-medium text-slate-400">Spd</th>
                <th class="text-right py-2 px-2 font-medium text-slate-400">Cad</th>
                <th class="text-right py-2 pl-2 font-medium text-slate-400">Dist</th>
                </tr>
            </thead>
            <tbody>'''
        sorted_players = sorted(leaderboard.items(), key=lambda x: x[1].get("distance",0), reverse=True)
        for i,(uid,data) in enumerate(sorted_players):
            user=db.child("users").child(uid).get().val()
            if not user: continue
            pos = f'''<span class="text-slate-300 text-[10px] mr-1 tabular-nums">{i+1}.</span>'''
            is_first = i==0
            res+=f'''<tr class="border-b border-slate-50">'''
            res+=f'''<td class="py-2.5 pr-2 font-medium text-slate-700">{pos}{user["name"]}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-500 tabular-nums">{data.get("avgHeartRate","--")}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-500 tabular-nums">{data.get("avgSpeed","--")}</td>'''
            res+=f'''<td class="py-2.5 px-2 text-right text-slate-500 tabular-nums">{data.get("avgCadence","--")}</td>'''
            res+=f'''<td class="py-2.5 pl-2 text-right font-semibold text-slate-800 tabular-nums">{round(data.get("distance",0),2)} mi</td>'''
            res+='''</tr>'''
        res+='''</tbody></table>'''
        return res
    return '''<p>Whaaaat?</p>'''

@components.route("/deviceDiv",methods=["GET"])
def deviceDiv():
    # Check if Web Bluetooth is available and warn if on insecure context
    bt_check = '''<script>
        (function(){
            var banner = document.getElementById("bt-warning");
            if (!banner) return;
            var msg = banner.querySelector("span");
            var isLocal = location.hostname === "localhost" || location.hostname === "127.0.0.1";
            var isSecure = location.protocol === "https:";
            var hasBT = !!navigator.bluetooth;

            if (!hasBT) {
                banner.style.display = "block";
                banner.className = "bg-amber-50 border border-amber-200 rounded-lg p-3 mb-3 flex items-start gap-2";
                // Check for common causes
                var ua = navigator.userAgent || "";
                var isAndroid = /Android/.test(ua);
                var isChrome = /Chrome/.test(ua) && !/Edge/.test(ua);
                var isIOS = /iPhone|iPad|iPod/.test(ua);
                if (isIOS) {
                    msg.innerHTML = "iOS does not support Web Bluetooth. No browser on iPhone/iPad can connect to Bluetooth sensors. Use an Android phone or a laptop with Chrome.";
                } else if (isAndroid && !isChrome) {
                    msg.innerHTML = "Web Bluetooth requires Chrome on Android. You appear to be using a different browser. Open this page in <strong>Google Chrome</strong>.";
                } else if (isAndroid && isChrome) {
                    msg.innerHTML = "Chrome on your device isn\'t exposing Web Bluetooth. Try: open <code style='background:#fef3c7;padding:1px 4px;border-radius:3px;font-size:11px'>chrome://flags</code>, search for <strong>Experimental Web Platform features</strong>, enable it, and restart Chrome.";
                } else {
                    msg.innerHTML = "Web Bluetooth is not supported in this browser. Use <strong>Google Chrome</strong> on Android, macOS, Windows, or ChromeOS.";
                }
            } else if (!isSecure && !isLocal) {
                banner.style.display = "block";
                banner.className = "bg-amber-50 border border-amber-200 rounded-lg p-3 mb-3 flex items-start gap-2";
                msg.innerHTML = "Bluetooth requires HTTPS. Open <code style='background:#fef3c7;padding:1px 4px;border-radius:3px;font-size:11px'>chrome://flags/#unsafely-treat-insecure-origin-as-secure</code>, enable it, add <strong>" + location.origin + "</strong>, and restart Chrome.";
            }
        })();
    </script>'''
    return '''<div class="bg-white rounded-xl ring-1 ring-slate-200 p-6">
            <div id="bt-warning" class="hidden" style="display:none">
                <svg class="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <span class="text-xs text-amber-700"></span>
            </div>
            <div class="flex items-center justify-between mb-3">
                <h2 class="text-sm font-semibold text-slate-800">Devices</h2>
                <button hx-get="/deviceForm" hx-target="#devices" hx-swap="afterbegin"
                    class="text-xs text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 font-medium py-1 px-2.5 rounded-md transition-colors">
                    + Add
                </button>
            </div>
            <div id="devices" class="space-y-2"></div>
        </div>''' + bt_check

@components.route("/deviceForm",methods=["GET"])
def deviceForm():
    return '''<form class="flex items-center gap-2 p-3 bg-slate-50 rounded-lg ring-1 ring-slate-200" onSubmit=addDevice(event)>
        <select id="type" name="type" class="flex-1 rounded-md border border-slate-200 px-3 py-2 text-xs text-slate-700 bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100">
            <option value=0>Heart Rate Monitor</option>
            <option value=1>Speed / Cadence Sensor</option>
        </select>
        <button class="bg-indigo-600 hover:bg-indigo-700 text-white w-7 h-7 rounded-md text-xs font-medium transition-colors flex items-center justify-center" type="submit">+</button>
        <button hx-get="/remove" hx-target="closest form" hx-swap="outerHTML" class="bg-white hover:bg-red-50 hover:text-red-500 text-slate-400 w-7 h-7 rounded-md text-xs transition-colors flex items-center justify-center ring-1 ring-slate-200" type="button">&times;</button>
    </form>'''

@components.route("/monitor",methods=["GET"])
def monitor():
    return '''
    <div class="bg-white rounded-xl ring-1 ring-slate-200 p-5">
        <h3 class="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">Live metrics</h3>
        <div class="grid grid-cols-4 gap-3">
            <div class="bg-slate-50 rounded-lg p-3 text-center">
                <p id="distance" class="text-xl font-semibold text-slate-800 tabular-nums">0.00</p>
                <p class="text-[10px] text-slate-400 mt-0.5 uppercase tracking-wider">mi</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-3 text-center">
                <p id="speed" class="text-xl font-semibold text-slate-800 tabular-nums">--</p>
                <p class="text-[10px] text-slate-400 mt-0.5 uppercase tracking-wider">mph</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-3 text-center">
                <p id="cadence" class="text-xl font-semibold text-slate-800 tabular-nums">--</p>
                <p class="text-[10px] text-slate-400 mt-0.5 uppercase tracking-wider">rpm</p>
            </div>
            <div class="bg-slate-50 rounded-lg p-3 text-center">
                <p id="hr" class="text-xl font-semibold text-slate-800 tabular-nums">--</p>
                <p class="text-[10px] text-slate-400 mt-0.5 uppercase tracking-wider">bpm</p>
            </div>
        </div>
    </div>'''

@components.route("/results/<string:room_id>",methods=["GET"])
def results(room_id):
    leaderboard = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").order_by_child("distance").limit_to_first(3).get().val()

    podium_html='''<div class="space-y-2">'''
    for i,player in enumerate(leaderboard):
        user_name = db.child("users").child(player).child("name").get().val()
        distance = leaderboard[player].get('distance',0)
        pos_bg = {0:"bg-yellow-50 text-yellow-700", 1:"bg-slate-100 text-slate-500", 2:"bg-amber-50 text-amber-700"}.get(i, "bg-slate-50 text-slate-400")
        podium_html+=f'''<div class="flex items-center justify-between rounded-lg px-4 py-3 {pos_bg}">
            <div class="flex items-center gap-3">
                <span class="text-xs font-semibold tabular-nums w-4">{i+1}</span>
                <span class="text-sm font-medium text-slate-800">{user_name}</span>
            </div>
            <span class="text-sm font-semibold text-slate-700">{round(distance,2)} mi</span>
        </div>'''
    podium_html+='''</div>'''

    stats = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").child(session['uid']).get().val()
    name = db.child("rooms").child("past_rooms").child(room_id).child("name").get().val()

    def stat_card(label, value):
        return f'''<div class="bg-slate-50 rounded-lg p-3 text-center"><p class="text-[10px] text-slate-400 uppercase tracking-wider">{label}</p><p class="text-lg font-semibold text-slate-800 mt-1">{value}</p></div>'''

    statDiv = stat_card("Heart Rate", stats.get("avgHeartRate","--"))
    statDiv += stat_card("Distance", stats.get("distance","--"))
    statDiv += stat_card("Cadence", stats.get("avgCadence","--"))
    statDiv += stat_card("Speed", stats.get("avgSpeed","--"))

    buttonDiv=f'''<div class="flex items-center justify-center gap-3">
        <a href="/download/{room_id}"
            class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium py-2.5 px-5 rounded-lg transition-colors">
            Download .FIT / .GPX
        </a>
        <button hx-get="/strava_login" hx-swap="outerHTML"
            class="bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium py-2.5 px-5 rounded-lg transition-colors">
            Upload to Strava
        </button>
    </div>'''

    return f'''<div>
        <div class="text-center mb-6">
            <h1 class="text-xl font-semibold text-slate-900 mb-1">{name}</h1>
            <p class="text-xs text-slate-400">Ride complete</p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">{statDiv}</div>
        <div class="mb-6">
            <h3 class="text-xs font-medium text-slate-400 uppercase tracking-wider mb-3">Podium</h3>
            {podium_html}
        </div>
        <div class="text-center">{buttonDiv}</div>
    </div>'''

@components.route("/history",methods=["GET"])
def history():
    uid = session['uid']
    history = db.child("users").child(uid).child("history").get().val()
    if not history:
        return '''<div class="text-center py-8">
            <p class="text-sm text-slate-400">No rides yet. Create or join a room to get started.</p>
        </div>'''
    res = '''<div class="space-y-1">'''
    for key in history:
        name = db.child("rooms").child("past_rooms").child(history[key]).child("name").get().val()
        timestamp = db.child("rooms").child("past_rooms").child(history[key]).child("start").get().val()
        if timestamp:
            d = datetime.fromtimestamp(int(timestamp)//1000)
            sd = d.strftime('%b %d, %Y &middot; %I:%M %p')
        else:
            sd = ""
        res+=f'''<div onclick="location.href='/history/{history[key]}'" class="flex items-center justify-between rounded-lg px-3 py-2.5 cursor-pointer transition-colors hover:bg-slate-50">
            <span class="text-sm text-slate-700">{name}</span>
            <span class="text-xs text-slate-400">{sd}</span>
        </div>'''
    res += '''</div>'''
    return res
