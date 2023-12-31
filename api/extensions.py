from flask_socketio import SocketIO 
import os
import pyrebase

socketio = SocketIO()

config={
  "apiKey": os.getenv("apiKey"),
  "authDomain": os.getenv("authDomain"),
  "databaseURL": os.getenv("databaseURL"),
  "storageBucket": os.getenv("storageBucket")
}
#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()