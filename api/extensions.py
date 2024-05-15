from flask_socketio import SocketIO 
import os
import pyrebase

socketio = SocketIO()

config={
  "apiKey": os.getenv("APIKEY"),
  "authDomain": os.getenv("AUTHDOMAIN"),
  "databaseURL": os.getenv("DATABASEURL"),
  "storageBucket": os.getenv("STORAGEBUCKET")
}
#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()