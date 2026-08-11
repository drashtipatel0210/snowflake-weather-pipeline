import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

CITY = "Phoenix"
LATITUDE = 33.4484
LONGITUDE = -112.0740

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "wind_speed_10m_max"
    ],
    "timezone": "America/Phoenix"
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()["daily"]

df = pd.DataFrame({
    "CITY": CITY,
    "WEATHER_DATE": data["time"],
    "TEMP_MAX": data["temperature_2m_max"],
    "TEMP_MIN": data["temperature_2m_min"],
    "PRECIPITATION_SUM": data["precipitation_sum"],
    "WIND_SPEED_MAX": data["wind_speed_10m_max"]
})

conn = snowflake.connector.connect(
    user="drashtipatel",
    password="Wj6AmurqXmjGLP9",
    account="FQQUZIM-YZ61228",
    warehouse="COMPUTE_WH",
    database="WEATHER_DB",
    schema="RAW"
   )

cur = conn.cursor()
cur.execute("SELECT CURRENT_USER(), CURRENT_ACCOUNT(), CURRENT_WAREHOUSE()")
print(cur.fetchone())

success, nchunks, nrows, output = write_pandas(
    conn,
    df,
    "DAILY_WEATHER"
)

print(f"Loaded {nrows} rows into Snowflake")
cur.close()
conn.close()