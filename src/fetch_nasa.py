import pandas as pd
import requests
import time

state_coords = { ... paste the dict from above ... }

def fetch_monthly(lat, lon, year):
    url = f"https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=PRECTOT&community=AG&longitude={lon}&latitude={lat}&start={year}&end={year}&format=JSON"
    r = requests.get(url).json()
    df = pd.DataFrame(r['properties']['parameter']['PRECTOT'], index=[0]).T
    df.index = pd.to_datetime(df.index, format="%Y%m")
    return df

def kharif_total(df):
    mm = df[df.index.month.isin([6,7,8,9])]
    # NASA gives mm/day → convert to mm/month
    mm_month = mm.apply(lambda x: x * x.index.days_in_month)
    return mm_month.sum().values[0]

rows = []
for state, (lat, lon) in state_coords.items():
    for year in range(2000, 2020):
        df = fetch_monthly(lat, lon, year)
        kh = kharif_total(df)
        rows.append((state, year, kh))
        time.sleep(0.6)  # NASA polite delay

rain_df = pd.DataFrame(rows, columns=["State","Year","Kharif_Rain_mm"])
rain_df.to_csv("data/raw/nasa_rainfall.csv", index=False)
