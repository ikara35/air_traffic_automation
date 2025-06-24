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

# 📌 Havalimanı koordinatları (İstanbul, İzmir, Antalya)
airport_coords = {
    "LTBA": (40.9769, 28.8146),
    "LTFM": (41.2753, 28.7519),
    "LTBJ": (38.2924, 27.1560),
    "LTAI": (36.8987, 30.8005)
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def check_approach(row):
    try:
        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]) or pd.isna(row["baro_altitude"]):
            return ""
        if row["baro_altitude"] > 4000:
            return ""
        results = []
        for name, (lat_airport, lon_airport) in airport_coords.items():
            distance = haversine(row["latitude"], row["longitude"], lat_airport, lon_airport)
            if distance < 100:
                results.append(name)
        return ",".join(results)
    except:
        return ""


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
df["retrieved_at_tr"] = retrieved_at_tr
df['callsign'] = df['callsign'].fillna('').str.strip()
df["velocity_kmh"] = df["velocity"] * 3.6
df["approaching_airports"] = df.apply(check_approach, axis=1)

# 🛢️ Veritabanına aktar
engine = create_engine(db_url)
df.to_sql("ucus_verisi", con=engine, if_exists="replace", index=False)

print("✅ Veri Neon PostgreSQL'e başarıyla yüklendi.")
