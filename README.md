# Leaderboard App

A virtual cycling leaderboard app that creates multiplayer rooms, connects to Bluetooth sensors for real-time ride data, and uploads completed rides to Strava.

**Stack:** Flask, HTMX, SocketIO, Firebase, Strava API, Web Bluetooth, C# .NET encoder

---

## External Services

The app depends on the following external services. You need accounts and credentials for each:

### 1. Firebase (Authentication & Realtime Database)
- **Purpose:** User login/signup, storing room state, leaderboard data, and ride history
- **Service:** [Firebase](https://console.firebase.google.com/)
- **SDK:** `pyrebase4` (Python), `FireSharp` (C# encoder)
- **Used features:**
  - Email/Password Authentication
  - Realtime Database (`rooms/current_rooms`, `rooms/past_rooms`, `users`)
- **Credentials needed** (set in `keys.env`):
  ```
  APIKEY          - Firebase Web API Key
  AUTHDOMAIN      - Firebase Auth Domain (e.g., leaderboard-app-XXXX.firebaseapp.com)
  DATABASEURL     - Firebase Realtime Database URL
  STORAGEBUCKET   - Firebase Storage Bucket
  ```

### 2. Strava API (Activity Upload)
- **Purpose:** OAuth-based login to upload completed rides (.FIT or .GPX files)
- **Service:** [Strava API](https://developers.strava.com/)
- **SDK:** `stravalib` (Python)
- **Credentials needed** (set in `keys.env`):
  ```
  SECRET  - Strava Client Secret
  ID      - Strava Client ID
  ```
- Your Strava API application must have the redirect URI pointing to your deployment's `/post_strava_login` endpoint

### 3. Encoder Service (C# .NET - Azure App Service)
- **Purpose:** Generates .FIT files from raw ride data stored in Firebase
- **Location:** `encoder/` directory
- **Deployed at:** `https://leaderboard-encoder.azurewebsites.net`
- **Stack:** ASP.NET Core minimal API, FireSharp (Firebase C# client), custom FIT encoder
- **API:** `GET /weatherforecast/{room_id}/{uid}` → returns a `.fit` file
- **Note:** The Flask app polls this service to get ride files before uploading to Strava

### 4. Web Bluetooth API (Browser-based Sensor Connection)
- **Purpose:** Connect to Bluetooth cycling sensors directly from the browser
- **Supported sensors:** Heart Rate Monitor, Speed/Cadence Sensor
- **Requirements:** Chrome on Android, macOS, Windows, or ChromeOS (iOS not supported)
- **Requires HTTPS in production** (except localhost)

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- Conda (recommended) or venv
- A Firebase project with Email/Password auth and Realtime Database enabled
- A Strava API application
- `.NET SDK 7+` (only needed for the encoder)

### 1. Clone & set up environment
```bash
cd api
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Create `keys.env` in the project root
```
export APIKEY=your_firebase_api_key
export AUTHDOMAIN=your_project.firebaseapp.com
export DATABASEURL=https://your_project-default-rtdb.firebaseio.com
export STORAGEBUCKET=your_project.appspot.com
export SECRET=your_strava_client_secret
export ID=your_strava_client_id
```

### 3. Run the Flask app
```bash
source ../keys.env
flask run -p 8000
```

### 4. Run the Encoder (optional, for .FIT file generation)
```bash
cd encoder/leaderboard_app_encoder
dotnet run
```
Without the encoder running, the app falls back to generating `.gpx` files for download/Strava upload.

---

## Deployment

### Flask App (api/)

#### Option A: Docker

**Build the Docker image:**
```bash
# From the project root, first generate the Dockerfile with env vars
python generateDockerfile.py

# Build
docker build -t leaderboard-api -f api/Dockerfile api/

# Run
docker run -p 8000:8000 leaderboard-api
```

#### Option B: Any Flask-compatible host

The app is a standard Flask app. Deploy to any service that supports Flask:
- **Azure App Service** (Python runtime)
  ```bash
  az webapp up --name leaderboard-api --runtime PYTHON:3.10 --sku B1
  ```
- **Railway / Render / Fly.io** — point at the `api/` directory, set environment variables from `keys.env`, and use `flask run -p 8000` as the start command
- **Heroku** — add a `Procfile`:
  ```
  web: flask run --host 0.0.0.0 --port $PORT
  ```

**Important:** In production you should:
- Use environment variables/secrets management rather than `keys.env`
- Set `app.config['SECRET_KEY']` to a strong random string
- Serve over HTTPS (required for Web Bluetooth sensor connections)
- Configure the Strava OAuth redirect URI to your production domain's `/post_strava_login`

### Encoder Service (encoder/)

The encoder is an ASP.NET Core minimal API. Deploy to:

#### Azure App Service (.NET runtime)
```bash
cd encoder/leaderboard_app_encoder
dotnet publish -c Release -o ./publish
cd publish
zip -r ../encoder.zip .
az webapp deploy --resource-group <rg> --name leaderboard-encoder --src-path ../encoder.zip
```

Set these environment variables on the App Service:
- `APIKEY` — Firebase Web API Key
- `DATABASEURL` — Firebase Realtime Database URL

After deployment, update the encoder URL in `api/app.py`:
```python
urllib.request.urlretrieve(f'https://YOUR_ENCODER_HOST/weatherforecast/{room_id}/{uid}', ...)
```

---

## Architecture Overview

```
┌──────────────┐     Web Bluetooth      ┌──────────────────┐
│   Browser    │◄──────────────────────►│ Cycling Sensors  │
│  (Chrome)    │    HR / Speed / Cad    │  (BLE devices)   │
└──────┬───────┘                        └──────────────────┘
       │ SocketIO / HTMX
       ▼
┌──────────────┐                         ┌──────────────────┐
│  Flask App   │── Firebase Auth ───────►│    Firebase      │
│  (api/)      │── Realtime Database ───►│  (Auth + RTDB)   │
└──────┬───────┘                         └──────────────────┘
       │ GET /weatherforecast/{rid}/{uid}
       ▼
┌──────────────┐                         ┌──────────────────┐
│  Encoder     │── Firebase RTDB ───────►│    Firebase      │
│  (C# .NET)   │   (reads ride data)     │    (RTDB)        │
└──────┬───────┘
       │ returns .FIT file
       ▼
┌──────────────┐
│  Flask App   │── OAuth + Upload ──────►│    Strava API    │
└──────────────┘                         └──────────────────┘
```

---

## Project Structure

```
leaderboard_app/
├── api/                        # Flask backend
│   ├── app.py                  # Main app, routes, auth
│   ├── components.py           # HTMX partial components
│   ├── events.py               # SocketIO real-time events
│   ├── extensions.py           # Firebase initialization (pyrebase4)
│   ├── pages.py                # Page routes (login, room, history)
│   ├── download_data.py        # Strava API helpers
│   ├── Dockerfile              # Docker config (auto-generated)
│   ├── requirements.txt        # Python dependencies
│   ├── static/
│   │   ├── Sensor.js           # Web Bluetooth sensor client
│   │   └── index.js            # Canvas rendering, socket, stopwatch
│   └── templates/              # Jinja2 HTML templates + partials
├── encoder/                    # C# .FIT encoder service
│   └── leaderboard_app_encoder/
│       ├── Program.cs          # ASP.NET minimal API
│       └── Encoder.cs          # FIT file generation logic
├── keys.env                    # Environment variables (gitignored)
└── README.md
```

---

## Bluetooth Sensor Setup

1. Open the app in **Chrome** (required for Web Bluetooth)
2. Enter a room
3. Click **+ Add** in the Devices panel
4. Select your sensor type (Heart Rate or Speed/Cadence)
5. Pair with your BLE sensor when prompted

**Troubleshooting:**
- iOS is **not supported** — no browser on iPhone/iPad supports Web Bluetooth
- On Android, Chrome needs **Location permission** to scan for Bluetooth
- Production deployments **must use HTTPS** (except localhost)
- If Bluetooth isn't detected, check `chrome://flags` → enable "Experimental Web Platform features"

---

## Firebase Database Structure

```
rooms/
├── current_rooms/
│   └── {room_number}/
│       ├── name: "Room name"
│       ├── host: uid
│       ├── state: "w" | "s" | "f"   (waiting, started, finished)
│       ├── start: timestamp
│       ├── id: past_room_key
│       ├── leaderboard/
│       │   └── {uid}/
│       │       ├── name: string
│       │       ├── distance: float (miles)
│       │       ├── avgSpeed: float
│       │       ├── avgHeartRate: float
│       │       ├── avgCadence: float
│       │       └── here: 0|1
│       ├── players/
│       │   └── {uid}/
│       │       └── {timestamp}/
│       │           ├── heartRate: int
│       │           ├── speed: float
│       │           ├── cadence: int
│       │           └── distance: float
│       └── kicked/{uid}: "1"
└── past_rooms/
    └── {room_key}/
        └── (same structure as current_rooms)
users/
└── {uid}/
    ├── name: string
    └── history/
        └── {key}: past_room_key
```
