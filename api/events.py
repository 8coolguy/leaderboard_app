from extensions import socketio
from flask import request,session
from statistics import mean

last_tick=0
begin=-1
tot=0
series=[]

@socketio.on("connect")
def handle_connect():
    print("Connected!")

@socketio.on("user_join")
def handle_user_join(username):
    user=session['name']
    print(f"User {username} {user} joined!")

@socketio.on("activity_tick")
def handle_activity_tick(data):
    global last_tick
    global begin
    global tot
    global series
    start=int(list(data.keys())[0])
    if begin==-1:
        begin=start
        tot=0
    tot+=data[str(start)]["heartRate"]
    series.append(data[str(start)]["heartRate"])
    delta = start-last_tick
    print(delta/1000)
    print(round((tot/((len(series))))))
    

    last_tick=start
@socketio.on("activity_start")
def handle_activity_start(start_time):
    #mark when activity started in current room and change state
    print("Activity Started",start_time)