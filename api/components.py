from extensions import firebase, auth, db
from flask import Blueprint, request, session
from flask_htmx import HTMX, make_response
from helper import getStopWatch


components =Blueprint('components',__name__,template_folder="templates")

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
        room=db.child("rooms").child("current_rooms").child(str(room_id)).get().val()
    
        
        if session['uid']==room['host']:
            # Generates the players and kick buttons
            for player in room['leaderboard'].keys():
                if player==room['host']:continue
                res+=f'''<div class="flex flex-col" id=res_{player}>'''
                if session['uid']==room['host']:
                    res+=f'''<button class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" hx-post="/kick" hx-target='#res_{player}' uid={player}>Kick {db.child("users").child(player).child('name').get().val()}</button>'''
                res+='</div>'

        
            res+=getStopWatch()
        return f'''<div class="flex justify-center"><div class="flex flex-col bg-amber-200 justify-center border-[6px] rounded-md tw-border-solid border-black items-center space-y-3 p-4">
            <h1 class="text-3xl">{room['name']}#{room_id}</h1>
            <p class="text-gray-600">Pin: {room_id}</p>
            <p>State: {room['state']}</p>''' + res + '''</div></div>'''
 
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
            res+=f'''<td> {leaderboard[uid].get("distance","--")}</td>'''
            res+='''</tr>'''
        res+='''</tbody>'''
        return f'''<p>Leaderboard for{room_id}</p>'''+res
    return '''<p>Whaaaat?</p>'''
@components.route("/deviceDiv",methods=["GET"])
def deviceDiv():
    room_id=request.referrer.split('/')[-1]
    host=db.child("rooms").child("current_rooms").child(str(room_id)).child('host').get().val()
    if session['uid']==host: return ''''''
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





