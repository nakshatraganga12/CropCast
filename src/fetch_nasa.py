import os
os.environ["PANDAS_NO_ARROW"] = "1"
import pandas as pd
import requests
import time

# State centroids for NASA POWER
state_coords = {
    "Andhra Pradesh": (16.50, 80.64),
    "Assam": (26.20, 92.93),
    "Bihar": (25.38, 85.09),
    "Chhattisgarh": (21.27, 81.60),
    "Gujarat": (22.69, 72.88),
    "Haryana": (29.05, 76.08),
    "Himachal Pradesh": (31.10, 77.17),
    "Jharkhand": (23.62, 85.50),
    "Karnataka": (15.31, 75.71),
    "Kerala": (10.85, 76.27),
    "Madhya Pradesh": (23.94, 78.88),
    "Maharashtra": (19.75, 75.71),
    "Odisha": (20.95, 85.10),
    "Punjab": (31.15, 75.34),
    "Rajasthan": (26.91, 75.79),
    "Tamil Nadu": (11.12, 78.65),
    "Telangana": (18.11, 79.01),
    "Uttar Pradesh": (26.85, 80.91),
    "Uttarakhand": (30.32, 79.02),
    "West Bengal": (23.69, 87.74),
}

def fetch_monthly(lat, lon, year):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
        f"parameters=PRECTOTCORR&community=AG"
        f"&longitude={lon}&latitude={lat}&start={year}&end={year}&format=JSON"
    )
    r = requests.get(url).json()
    
    df = pd.DataFrame(r['properties']['parameter']['PRECTOTCORR'], index=[0]).T

    # remove NASA "13th month" annual summary
    df = df[df.index.str[-2:] != "13"]

    # now parse into datetime
    df.index = pd.to_datetime(df.index, format="%Y%m")
    
    return df


def kharif_total(df):
    mm = df[df.index.month.isin([6,7,8,9])]
    mm_month = mm.apply(lambda x: x * x.index.days_in_month)
    return mm_month.sum().values[0]

rows = []

for state, (lat, lon) in state_coords.items():
    for year in range(2000, 2020):
        df = fetch_monthly(lat, lon, year)
        kh = kharif_total(df)
        rows.append((state, year, kh))
        print(f"{state} {year}: {kh:.2f} mm")
        time.sleep(0.5)  # NASA rate limit comfort

rain_df = pd.DataFrame(rows, columns=["State", "Year", "Kharif_Rain_mm"])
rain_df.to_csv("data/raw/nasa_rainfall.csv", index=False)

print("✔ Saved → data/raw/nasa_rainfall.csv")
