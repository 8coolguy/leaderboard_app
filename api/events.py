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
    room_id=request.referrer.split("/")[-1]
    db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update({"here":1})
    print(f"User {username} {user} joined!")
    send(f'''<p>{username}</p>''')
@socketio.on("user_leave")
def handle_user_leave():
    room_id=request.referrer.split("/")[-1]
    db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update({"here":0})
    leave_room(room_id)
    print(session['name']+" left.")
# @socketio.on("activity_tick")
# def handle_activity_tick(data):
    
#     room_id=request.referrer.split("/")[-1]
    
#     if db.child("rooms").child("current_rooms").child(room_id).child('state').get().val() != 's':
#         # print("Hasnt Started")
#         return
#     player=db.child("rooms").child("current_rooms").child(room_id).child("players").child(session["uid"]).get()
#     player_leaderboard = db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).get().val()
    

#     start = int(list(data.keys())[0])
    
#     response = dict()
#     if "heartRate" in data[str(start)]: 
#         player.child(start//1000).set({"heartRate":data[str(start)]["heartRate"]})
#         totalMetric = player_leaderboard.get("totalHeartRate",0)
#         totalCount = player_leaderboard.get("totalHeartRateCount",0)
#         response["heartRate"] = data[str(start)]["heartRate"]
#         totalCount +=1
#         totalMetric += data[str(start)]["heartRate"]
#     if "speed" in data[str(start)]:
#         player.child(start//1000).set({"speed":data[str(start)]["speed"]})
#         totalMetric = player_leaderboard.get("totalSpeed",0)
#         totalCount = player_leaderboard.get("totalSpeedCount",0)
#         response["heartRate"] = data[str(start)]["heartRate"]
#         totalCount +=1
#         totalMetric += data[str(start)]["heartRate"]
#     if "cadence" in data[str(start)]: 
#         player.child(start//1000).set({"cadence":data[str(start)]["cadence"]})
#     if response:
#         db.child("rooms").child("current_rooms").child(room_id).child("players").child(session["uid"]).child(start//1000).set(response)
    
#     avg_heartrate=totalMetric/totalCount
#     db.child("rooms").child("current_rooms").child(room_id).child("leaderboard").child(session["uid"]).update({
#         "avgHeartRate":avg_heartrate,
#         "totalHeartRate":totalMetric,
#         "totalHeartRateCount":totalCount
#         })
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
