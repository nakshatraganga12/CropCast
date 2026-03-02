import pandas as pd

# Load datasets
yield_df = pd.read_csv("data/raw/dld_yield.csv")
rain_df = pd.read_csv("data/raw/nasa_rainfall.csv")

# Clean column names
yield_df = yield_df.rename(columns={
    "State Name": "State",
    "Yield (t/ha)": "Yield_t_ha",
    "SUM of RICE AREA (1000 ha)": "Area_1000ha",
    "SUM of RICE PRODUCTION (1000 tons)": "Prod_1000t"
})

# Optional: convert year to int for safety
yield_df["Year"] = yield_df["Year"].astype(int)
rain_df["Year"] = rain_df["Year"].astype(int)

# Merge panel
merged = pd.merge(yield_df, rain_df, on=["State", "Year"], how="inner")

# Save
merged.to_csv("data/processed/merged_panel.csv", index=False)

print("✔ Merged panel saved → data/processed/merged_panel.csv")
print(merged.head())
