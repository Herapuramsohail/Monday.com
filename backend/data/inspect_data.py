import pandas as pd
import json

df_deals = pd.read_csv(r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\deal_funnel.csv")
df_work = pd.read_csv(r"C:\Users\Muskan\.gemini\antigravity\scratch\monday-bi-agent\data\work_order_tracker.csv")

print("--- DEAL FUNNEL COLUMNS ---")
print(df_deals.columns.tolist())
print("\n--- DEAL FUNNEL HEAD ---")
print(df_deals.head(3).to_dict(orient='records'))

print("\n--- WORK ORDER TRACKER COLUMNS ---")
print(df_work.columns.tolist())
print("\n--- WORK ORDER TRACKER HEAD ---")
print(df_work.head(3).to_dict(orient='records'))

print("\n--- DEAL FUNNEL SHAPE ---", df_deals.shape)
print("--- WORK ORDER TRACKER SHAPE ---", df_work.shape)
