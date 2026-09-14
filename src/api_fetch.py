import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

all_records = []

today = datetime.now()

start_date = today - relativedelta(years=5)
end_date = today

all_records = []

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"


# Start from the year of our start date
for year in range(start_date.year, end_date.year + 1):

    for month in range(1, 13):

        # First day of this month
        month_start = datetime(year, month, 1)

        # Skip months before our start date
        if month_start < start_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ):
            continue

        # Stop after our end date
        if month_start > end_date:
            break

        # Calculate next month
        month_end = month_start + relativedelta(months=1)

        # Don't go beyond our actual end date
        if month_end > end_date:
            month_end = end_date

        params = {
            "format": "geojson",
            "starttime": month_start.isoformat(),
            "endtime": month_end.isoformat(),
            "minmagnitude": 3,
            "limit": 20000,
            "orderby": "time"
        }
        try:
            response = requests.get(
                url,
                params=params,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print("Error fetching data from USGS API:", e)
            continue

        for f in data["features"]:

            p = f["properties"]
            g = f["geometry"]["coordinates"]

            all_records.append({
                "id": f.get("id"),
                "time": pd.to_datetime(
                    p.get("time"),
                    unit="ms"
                ),
                "updated": pd.to_datetime(
                    p.get("updated"),
                    unit="ms"
                ),
                "latitude": g[1] if g else None,
                "longitude": g[0] if g else None,
                "depth_km": g[2] if g else None,
                "mag": p.get("mag"),
                "magType": p.get("magType"),
                "place": p.get("place"),
                "status": p.get("status"),
                "tsunami": p.get("tsunami"),
                "sig": p.get("sig"),
                "net": p.get("net"),
                "nst": p.get("nst"),
                "dmin": p.get("dmin"),
                "rms": p.get("rms"),
                "gap": p.get("gap"),
                "type": p.get("type"),
                "alert": p.get("alert"),
                "felt":p.get("felt"),
                "cdi":p.get("cdi"),
                "mmi":p.get("mmi"),
                "code":p.get("code"),
                "types":p.get("types"),
                "ids":p.get("ids"),
                "sources":p.get("sources"),
                "type":p.get("type")
            })


df = pd.DataFrame(all_records)
df.to_csv("data/earthquakes_raw.csv", index=False)


