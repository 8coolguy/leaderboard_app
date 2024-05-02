from extensions import socketio
from flask_socketio import emit,send,join_room,leave_room
from flask import request,session
from statistics import mean
from extensions import db
import datetime
import calendar

@socketio.on("connect")
def handle_connect():
    room_id=request.referrer.split("/")[-1]
    join_room(room_id)
    emit("response","Connected!"+session['name'],to=room_id)
    room=db.child("rooms").child("current_rooms").child(room_id)
    if room.child("state").get().val()=="s":
        start_time = db.child("rooms").child("current_rooms").child(room_id).child("start").get().val()
        emit("start",start_time,broadcast=False)
@socketio.on("user_join")
def handle_user_join(username):
    user=session['name']
    room_id=request.referrer.split("/")[-1]
    db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update({"here":1})
    print(f"User {username} {user} joined!")
    # send(f'''<p>{username}</p>''')
@socketio.on("user_leave")
def handle_user_leave():
    room_id=request.referrer.split("/")[-1]
    db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update({"here":0})
    leave_room(room_id)
    print(session['name']+" left.")
@socketio.on("activity_tick")
def handle_activity_tick(data):
    
    room_id=request.referrer.split("/")[-1]

    #returns if room is not in a started state
    if db.child("rooms").child("current_rooms").child(room_id).child('state').get().val() != 's':
        return
    
    player_leaderboard = db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).get().val()
    start = int(list(data.keys())[0])
    
    response = dict()
    leaderboardResponse = dict()
    if "heartRate" in data[str(start)]: 
        totalHr = player_leaderboard.get("totalHeartRate",0)
        totalHrCount = player_leaderboard.get("totalHeartRateCount",0)
        response["heartRate"] = data[str(start)]["heartRate"]
        totalHrCount +=1
        totalHr += data[str(start)]["heartRate"]
        leaderboardResponse["avgHeartRate"]=round(totalHr/totalHrCount,2)
        leaderboardResponse["totalHeartRate"]=totalHr
        leaderboardResponse["totalHeartRateCount"]=totalHrCount
    if "speed" in data[str(start)]:
        distance = player_leaderboard.get("distance",0)
        totalSpeed = player_leaderboard.get("totalSpeed",0)
        totalSpeedCount = player_leaderboard.get("totalSpeedCount",0)
        response["speed"] = data[str(start)]["speed"]
        totalSpeedCount +=1
        totalSpeed += data[str(start)]["speed"]
        leaderboardResponse["avgSpeed"]=round(totalSpeed/totalSpeedCount,2)
        leaderboardResponse["totalSpeed"]=totalSpeed
        leaderboardResponse["totalSpeedCount"]=totalSpeedCount
        leaderboardResponse["distance"] = distance + data[str(start)]["distance"]
    if "cadence" in data[str(start)]: 
        totalCad = player_leaderboard.get("totalCad",0)
        totalCadCount = player_leaderboard.get("totalCadCount",0)
        response["cadence"] = data[str(start)]["cadence"]
        totalCadCount +=1
        totalCad += data[str(start)]["cadence"]
        leaderboardResponse["avgCadence"]=round(totalCad/totalCadCount,2)
        leaderboardResponse["totalCad"]=totalCad
        leaderboardResponse["totalCadCount"]=totalCadCount
    if response and leaderboardResponse:
        db.child("rooms").child("current_rooms").child(room_id).child("players").child(session["uid"]).child(start//1000).update(response)
        db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update(leaderboardResponse)
@socketio.on("activity_start")
def handle_activity_start(start_time):
    #mark when activity started in current room and change state
    print("Activity Started",start_time)
    room_id=request.referrer.split("/")[-1]
    room=db.child("rooms").child("current_rooms").child(room_id)
    if room.child("state").get().val()=="w":
        db.child("rooms").child("current_rooms").child(room_id).update({"state":"s"})
        db.child("rooms").child("current_rooms").child(room_id).update({"start":start_time})
        emit("start",start_time,to=room_id)
        
@socketio.on("activity_end")
def handle_activity_end(end_time):
    print("Activity Ended",end_time) 
    room_id=request.referrer.split("/")[-1]
    room=db.child("rooms").child("current_rooms").child(room_id)
    if room.child("state").get().val()=="s":
        db.child("rooms").child("current_rooms").child(room_id).update({"state":"f"})
        db.child("rooms").child("current_rooms").child(room_id).update({"end":end_time})
        emit("end","hello",to=room_id)

