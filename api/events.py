from extensions import socketio
from flask_socketio import emit,send,join_room,leave_room
from flask import request,session
from statistics import mean
from extensions import db

last_tick=0
begin=-1
tot=0
series=[]

@socketio.on("connect")
def handle_connect():
    room_id=request.referrer.split("/")[-1]
    join_room(room_id)
    emit("response","Connected!"+session['name'],to=room_id)
@socketio.on("user_join")
def handle_user_join(username):
    user=session['name']
    print(f"User {username} {user} joined!")
    send(f'''<p>{username}</p>''')
@socketio.on("user_leave")
def handle_user_leave():
    room_id=request.referrer.split("/")[-1]
    leave_room(room_id)
    print(session['name']+" left.")
@socketio.on("activity_tick")
def handle_activity_tick(data):
    global last_tick
    global begin
    global tot
    global series
    room_id=request.referrer.split("/")[-1]
    start=int(list(data.keys())[0])
    player=db.child("rooms").child("current_rooms").child(room_id).child("players").child(session['uid'])
    
    if "heartRate" in data[str(start)]: player.child(start//1000).set({"heartRate":data[str(start)]["heartRate"]})
    # if "speed" in data[str(start)]: player.child(start//1000).set({"speed":data[str(start)]["speed"]})
    # if "cadence" in data[str(start)]: player.child(start//1000).set({"cadence":data[str(start)]["cadence"]})
    return
    if begin==-1:
        begin=start
        tot=0
    tot+=data[str(start)]["heartRate"]
    series.append(data[str(start)]["heartRate"])
    # delta = start-last_tick
    avg_heartrate=round((tot/((len(series)))))
    
    db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).set({"avgHeartRate":avg_heartrate})
    last_tick=start
@socketio.on("activity_start")
def handle_activity_start(start_time):
    #mark when activity started in current room and change state
    print("Activity Started",start_time)
    room_id=request.referrer.split("/")[-1]
    room=db.child("rooms").child("current_rooms").child(room_id)
    if room.child("state").get().val()=="w":
        room.child("rooms").child("current_rooms").child(room_id).update({"state":"s"})
        
@socketio.on("activity_end")
def handle_activity_end(end_time):
    print("Activity Ended",end_time) 
    room_id=request.referrer.split("/")[-1]
    room=db.child("rooms").child("current_rooms").child(room_id)
    if room.child("state").get().val()=="s":
        room.child("rooms").child("current_rooms").child(room_id).update({"state":"f"})
