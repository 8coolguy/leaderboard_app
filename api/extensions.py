from flask_socketio import SocketIO 
import os
import pyrebase

socketio = SocketIO()

config={
  "APIKEY": os.getenv("APIKEY"),
  "AUTHDOMAIN": os.getenv("AUTHDOMAIN"),
  "DATABASEURL": os.getenv("DATABASEURL"),
  "STORAGEBUCKET": os.getenv("STORAGEBUCKET")
}
#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()