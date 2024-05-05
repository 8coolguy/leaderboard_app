from extensions import firebase, auth, db
from flask import Blueprint, request, session
from flask_htmx import HTMX, make_response
from helper import getStopWatch, getStopWatchControl
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
# This function returns the html component that displays the leaderboard info at the right side of the screen.
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
    
        
        if session['uid']==host:
            # Generates the players and kick buttons
            for player in players:
                if player==host:continue
                res+=f'''<div class="flex flex-col" id=res_{player}>'''
                if session['uid']==host:
                    res+=f'''<button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" hx-post="/kick" hx-target='#res_{player}' uid={player}>Kick {db.child("users").child(player).child('name').get().val()}</button>'''
                res+='</div>'
            res+=getStopWatchControl()
        else:
            res+=getStopWatch()
        return f'''<div class="flex justify-center"><div class="flex flex-col bg-amber-200 justify-center border-[6px] rounded-md tw-border-solid border-black items-center space-y-3 p-4">
            <h1 class="text-3xl">{name}#{room_id}</h1>
            <p class="text-gray-600">Pin: {room_id}</p>
            <p>State: {state}</p>''' + res + '''</div></div>'''
 
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
    res='''<table class="table-auto border-separate border-spacing-2 bg-amber-200 rounded border-black border-[6px]">
        <thead>
            <tr>
            <th>Player</th>
            <th>Avg. Heart Rate</th>
            <th>Avg. Speed</th>
            <th>Avg. Cadence</th>
            <th>Distance</th>
            </tr>
        </thead>
        <tbody>'''
    if not session.get("is_logged_in",False):
        pass
    if request.method=="GET":
        leaderboard=db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").get().val()
        for i,uid in enumerate(leaderboard.keys()):
            user=db.child("users").child(uid).get().val()
            res+='''<tr>'''
            res+=f'''<td>{user["name"]}</td>'''
            res+=f'''<td> {leaderboard[uid].get("avgHeartRate","--")}</td>'''
            res+=f'''<td> {leaderboard[uid].get("avgSpeed","--")}</td>'''
            res+=f'''<td> {leaderboard[uid].get("avgCadence","--")}</td>'''
            res+=f'''<td> {round(leaderboard[uid].get("distance",0),2)}</td>'''
            res+='''</tr>'''
        res+='''</tbody>'''
        return res
    return '''<p>Whaaaat?</p>'''
@components.route("/deviceDiv",methods=["GET"])
def deviceDiv():
    room_id=request.referrer.split('/')[-1]
    host=db.child("rooms").child("current_rooms").child(str(room_id)).child('host').get().val()
    # if session['uid']==host: return ''''''
    return '''<div class="flex flex-col justify-center items-center bg-amber-200 border-[6px] rounded-md tw-border-solid border-black">
            <h1 class="text-xl">Devices</h1>
            <div id="devices" class="grid grid-cols-1 gap-4">

            </div>
            <button hx-get="/deviceForm" hx-target="#devices" hx-swap="afterbegin" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded" type="button">Add Device</button>
        </div>'''

@components.route("/deviceForm",methods=["GET"])
def deviceForm():
    return '''<form class="flex" onSubmit=addDevice(event)>
        <div class="p-1">
            <div class="mt-2">
                <select id="type" name="type" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6">
                    <option value=0>Heart Rate</option>
                    <option value=1>Cycling/Speed</option>
                </select>
            </div>
        </div>
        <div class="grid grid-cols-1">
            <button class="bg-green-500 hover:bg-green-700 text-white font-bold h-5 w-5 rounded" type="submit">✓</button>
            <button hx-get="/remove" hx-target="closest form" hx-swap="outerHTML" class="bg-red-500 hover:bg-red-700 text-white font-bold h-5 w-5 rounded" type="button">x</button>
        </div>
    </form>'''
@components.route("/monitor",methods=["GET"])
def monitor():
    room_id=request.referrer.split('/')[-1]
    host=db.child("rooms").child("current_rooms").child(str(room_id)).child('host').get().val()
    # if session['uid']==host: return ''''''
    return '''
    <div class="rounded border-[6px] border-black font-mono">
        <div class="flex-col border border-black">
            <div class="grid grid-cols-1 p-3">
                <p id = "distance"></p>
                <p>miles</p></div>
            </div>
            <div class="grid grid-cols-3 ">
                <div class="border border-black p-3">
                    <p id = "cadence"></p>
                    <p>rpm</p></div>
                <div class="border border-black p-3">
                    <p id = "hr"></p>
                    <p>bpm</p></div>
                <div class="border border-black p-3">
                    <p id = "speed"></p>
                    <p>mph</p>
                </div>
            </div>
        </div>
    </div>'''
@components.route("/results/<string:room_id>",methods=["GET"])
def results(room_id):
    leaderboard = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").order_by_child("distance").limit_to_first(3).get().val()
    res='''<table class="table-auto">
        <thead>
            <tr>
            <th>Place</th>
            <th>Player</th>
            <th>Distance</th>
            </tr>
        </thead>
        <tbody>'''
    for i,player in enumerate(leaderboard):
        res+='''<tr>'''
        res+=f'''<td> {i+1}</td>'''
        res+=f'''<td> {db.child("users").child(player).child("name").get().val()}</td>'''
        res+=f'''<td> {leaderboard[player].get('distance',0)}</td>'''
        res+='''</tr>'''
    res+='''</tbody>'''
    stats = db.child("rooms").child("past_rooms").child(room_id).child("leaderboard").child(session['uid']).get().val()
    name =db.child("rooms").child("past_rooms").child(room_id).child("name").get().val()
    statDiv=f''''''
    statDiv+=f'''<div class="flex flex-col p-3"><p class="font-bold">Heart Rate</p><p>{stats.get("avgHeartRate","--")}</p></div>'''
    statDiv+=f'''<div class="flex flex-col p-3"><p class="font-bold">Distance</p><p>{stats.get("distance","--")}</p></div>'''
    statDiv+=f'''<div class="flex flex-col p-3"><p class="font-bold">Cadence</p><p>{stats.get("avgCadence","--")}</p></div>'''
    statDiv+=f'''<div class="flex flex-col p-3"><p class="font-bold">Speed</p><p>{stats.get("avgSpeed","--")}</p></div>'''

    buttonDiv=''''''
    buttonDiv+=f'''<button hx-get="/strava_login" hx-swap="outerHTML" class="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" >Upload</button>'''
    return f'''<div class="justify-center p-5 border-separate border-spacing-2 bg-amber-200 rounded border-black border-[6px]">
        <h1 class="text-3xl">{name}</h1>
        <div class="flex justify-center p-3">{statDiv}</div>
        {res}
        <div class="flex justify-center p-3">{buttonDiv}</div>
    </div>'''
@components.route("/history",methods=["GET"])
def history():
    res = f''''''
    uid =session['uid']
    history = db.child("users").child(uid).child("history").get().val()
    for key in history:
        name = db.child("rooms").child("past_rooms").child(history[key]).child("name").get().val()
        print(history[key])
        timestamp = db.child("rooms").child("past_rooms").child(history[key]).child("start").get().val()
        d = datetime.fromtimestamp(int(timestamp)//1000)
        sd = d.strftime('%B %d,%Y %I:%M %p')
        res+=f'''<p onclick="location.href='/history/{history[key]}'">{name} on {sd}</p>'''
    return res

        
    
    





