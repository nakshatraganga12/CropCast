import pandas as pd

df = pd.read_csv("data/raw/dld_yield.csv")

df['Yield_t_ha'] = df['Prod_1000tons']*1000 / (df['Area_1000ha']*1000)

yield_df = df.groupby(['State','Year'])['Yield_t_ha'].mean().reset_index()

yield_df.to_csv("data/raw/yield_processed.csv", index=False)
