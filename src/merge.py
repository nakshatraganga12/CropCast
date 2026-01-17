import pandas as pd

rain = pd.read_csv("data/raw/nasa_rainfall.csv")
yield_df = pd.read_csv("data/raw/yield_processed.csv")

merged = rain.merge(yield_df, on=["State","Year"])
merged.to_csv("data/processed/rice_climate_panel.csv", index=False)
