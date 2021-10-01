import pandas as pd
import os
import matplotlib.pyplot as plt

DATA_SOURCE = os.path.join(os.getcwd(), "Data")
INV_DB = os.path.join(DATA_SOURCE, "tyre_inventory_db.csv")
INV_IN_DB = os.path.join(DATA_SOURCE, "tyre_inventory_in_db.csv")
TRACK_DB = os.path.join(DATA_SOURCE, "tyre_tracking_db.csv")

inv = pd.read_csv(INV_IN_DB, parse_dates=['Datetime'])
trk = pd.read_csv(TRACK_DB, parse_dates=['Date'])

inv['Date'] = pd.to_datetime(inv['Datetime'].dt.date)

df = pd.DataFrame(trk.pivot_table(values='Tyre_Size', index='Date', columns='Tyre_Name', aggfunc='count').to_records())
df.set_index('Date', inplace=True)
df = df * -1
df.reset_index(inplace=True)
df = df.append(pd.DataFrame(inv.pivot_table(values='Quantity', index='Date', columns='Tyre_Name', aggfunc='sum', fill_value=0).to_records()))

df.sort_values(['Date'], inplace=True)
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Month'] = df['Month'].apply(lambda x: "0{}".format(x) if x<10 else str(x))
df['Time'] = df['Year'].astype("str") + "-" + df['Month'].astype("str")

df.drop(['Date','Year','Month'], inplace=True, axis=1)

pv = df.pivot_table(values=inv['Tyre_Name'].unique(), index=df['Time'], aggfunc='sum')
pv = pv.cumsum()
pv.to_csv("Data/tyre_inventory_db.csv")
