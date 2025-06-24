import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from math import radians, cos, sin, asin, sqrt 

# ✈️ Coordinates of major Turkish airports (Istanbul, Izmir, Antalya)
# Used for detecting approaching aircraft based on distance and altitude
airport_coords = {
    "LTBA": (40.9769, 28.8146),  # Istanbul Ataturk Airport
    "LTFM": (41.2753, 28.7519),  # Istanbul Airport
    "LTBJ": (38.2924, 27.1560),  # Izmir Adnan Menderes Airport
    "LTAI": (36.8987, 30.8005)   # Antalya Airport
}

# 📏 Haversine formula to calculate great-circle distance between two lat/lon points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

# 🚦 Determine if aircraft is approaching one of the defined airports
def check_approach(row):
    try:
        lat = row.get("latitude")
        lon = row.get("longitude")
        alt = row.get("baro_altitude") or row.get("geo_altitude")  # fallback to geo altitude if barometric is missing

        if pd.isna(lat) or pd.isna(lon) or pd.isna(alt):
            return ""
        if row.get("on_ground") in [True, 't', 'T', 'true', 1]:  # skip aircraft already on ground
            return ""
        if alt > 4000:  # only consider aircraft below 4000 meters
            return ""

        results = []
        for name, (lat_ap, lon_ap) in airport_coords.items():
            distance = haversine(lat, lon, lat_ap, lon_ap)
            if distance < 100:  # Aircraft is within 100 km of airport
                results.append(name)
        return ",".join(results)
    except Exception as e:
        print(f"[check_approach] Error: {e}")
        return ""

# 🔐 Load credentials from GitHub Actions environment variables
client_id = os.getenv("OPEN_SKY_CLIENT_ID")
client_secret = os.getenv("OPEN_SKY_CLIENT_SECRET")
db_url = os.getenv("NEON_DB_URL")

# 🎟️ Request access token using OpenSky's OAuth2 client credentials flow
token_response = requests.post("https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token", data={
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
})
access_token = token_response.json()["access_token"]

# 🌍 Define the geographic bounding box for Turkey airspace
params = {"lamin": 35.0, "lamax": 43.0, "lomin": 25.0, "lomax": 45.0}
headers = {"Authorization": f"Bearer {access_token}"}

# 📡 Retrieve live flight data from OpenSky Network API
response = requests.get("https://opensky-network.org/api/states/all", headers=headers, params=params)
data = response.json()

# ✍️ Define expected columns from API response
columns = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source"
]
df = pd.DataFrame(data.get("states", []), columns=columns)

# ⏰ Add timestamp columns for logging and filtering
retrieved_at_utc = datetime.now(timezone.utc)
retrieved_at_tr = retrieved_at_utc + timedelta(hours=3)  # Turkish local time

df["retrieved_at"] = retrieved_at_utc
df["retrieved_at_tr"] = retrieved_at_tr

# 🧹 Data preprocessing: clean callsigns and convert velocity to km/h
df['callsign'] = df['callsign'].fillna('').str.strip()
df["velocity_kmh"] = df["velocity"] * 3.6

# 🛬 Calculate which aircraft are approaching any of the predefined airports
df["approaching_airports"] = df.apply(check_approach, axis=1)

# 💾 Save processed data into Neon.tech PostgreSQL table
engine = create_engine(db_url)
df.to_sql("ucus_verisi", con=engine, if_exists="replace", index=False)

print("✅ Flight data successfully written to Neon PostgreSQL database.")

