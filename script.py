import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine

# 🔐 Secrets from GitHub Actions
client_id = os.getenv("OPEN_SKY_CLIENT_ID")
client_secret = os.getenv("OPEN_SKY_CLIENT_SECRET")
db_url = os.getenv("NEON_DB_URL")

# 🎫 Token alma
token_response = requests.post("https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token", data={
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
})
access_token = token_response.json()["access_token"]

# 📡 API'den veri çek
params = {"lamin": 35.0, "lamax": 43.0, "lomin": 25.0, "lomax": 45.0}
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("https://opensky-network.org/api/states/all", headers=headers, params=params)
data = response.json()

columns = [
    "icao24", "callsign", "origin_country", "time_position", "last_contact",
    "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
    "true_track", "vertical_rate", "sensors", "geo_altitude", "squawk",
    "spi", "position_source"
]
df = pd.DataFrame(data.get("states", []), columns=columns)
retrieved_at_utc = datetime.now(timezone.utc)
retrieved_at_tr = retrieved_at_utc + timedelta(hours=3)

df["retrieved_at"] = retrieved_at_utc
df["retrieved_at_TR"] = retrieved_at_tr
df['callsign'] = df['callsign'].fillna('').str.strip()
df["velocity_kmh"] = df["velocity"] * 3.6

# 🛢️ Veritabanına aktar
engine = create_engine(db_url)
df.to_sql("ucus_verisi", con=engine, if_exists="append", index=False)

print("✅ Veri başarıyla yüklendi.")
