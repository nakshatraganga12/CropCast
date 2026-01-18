import pandas as pd
import requests
import time

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
    "West Bengal": (23.69, 87.74)
}

def fetch_monthly(lat, lon, year):
    url = (
        f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
        f"parameters=PRECTOTCORR&community=AG"
        f"&longitude={lon}&latitude={lat}"
        f"&start={year}&end={year}&format=JSON"
    )

    response = requests.get(url)
    response.raise_for_status()
    r = response.json()

    data = r["properties"]["parameter"]["PRECTOTCORR"]

    cleaned = {}

    for k, v in data.items():
        # Keep only YYYYMM format
        if len(k) == 6 and k.isdigit():
            year_part = int(k[:4])
            month_part = int(k[4:])

            # Keep only valid months 1–12
            if 1 <= month_part <= 12:
                cleaned[k] = v

    df = pd.DataFrame(cleaned, index=[0]).T
    df.index = pd.to_datetime(df.index, format="%Y%m")

    return df


def kharif_total(df):
    # Filter June–September
    monsoon = df[df.index.month.isin([6, 7, 8, 9])]

    # Convert mm/day → mm/month
    monsoon_mm = monsoon.apply(
        lambda col: col * col.index.days_in_month
    )

    return monsoon_mm.sum().values[0]


rows = []

for state, (lat, lon) in state_coords.items():
    print(f"Fetching {state}...")
    for year in range(2000, 2020):
        try:
            df = fetch_monthly(lat, lon, year)
            kh = kharif_total(df)
            rows.append((state, year, kh))
            time.sleep(0.6)  # NASA polite delay
        except Exception as e:
            print(f"Error for {state}, {year}: {e}")
            continue


rain_df = pd.DataFrame(
    rows,
    columns=["State", "Year", "Kharif_Rain_mm"]
)

rain_df.to_csv("data/raw/nasa_rainfall.csv", index=False)

print("NASA rainfall data successfully saved.")