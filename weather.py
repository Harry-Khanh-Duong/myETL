#import os
#from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import date, datetime
from sqlalchemy import Table,MetaData,create_engine,delete,text
#url = "https://api.open-meteo.com/v1/forecast" #for current data
url = "https://archive-api.open-meteo.com/v1/era5" #for historical data
params = {
    "latitude": 10.82,
    "longitude": 106.63,
    "start_date": "2022-01-01", # comment if retrieve forecast data
    "end_date": "2024-12-31", # comment if retrieve forecast data
    "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,rain",
    "daily": "moon_phase",
#    "forecast_days": 1, # comment if retrieve historical data
    "timezone": "auto"
}

response = requests.get(url, params=params).json()
print("Request successfully")
# Extract the 'current' dictionary
hourly_data = response["hourly"]
df = pd.DataFrame(hourly_data)
#df = df[df['time'] == datetime.now().replace(minute=0,second=0,microsecond=0).strftime("%Y-%m-%dT%H:%M")] # comment if using historical data
df['time'] = pd.to_datetime(df['time'])
df['date'] = df['time'].dt.date
df = df.sort_values('time',ascending=False)
print(df.head())
daily_data = response["daily"]
df2 = pd.DataFrame(daily_data)
df2['time'] = pd.to_datetime(df2['time']).dt.date
df = pd.merge(df,df2,how="left",left_on='date',right_on='time')
df = df[['time_x', 'temperature_2m', 'relative_humidity_2m', 'wind_speed_10m', 'moon_phase','rain']]
df.columns = ['time','temperature','humidity','wind','moonphase','rain']
df['year'] = df['time'].dt.year
df['day'] = df['time'].dt.day
df['month'] = df['time'].dt.month
df['hour'] = df['time'].dt.time
df = df.sort_values(by=['year']).reset_index(drop=True)
df['nxt_yr'] = df.groupby(['month','day','hour'])['temperature'].shift(-1)
df = df[['time','temperature','humidity','wind','moonphase','rain','nxt_yr']]
print("Transform successfully")
#Full Load data to Database
#load_dotenv()
#password = os.getenv("DB_PASSWORD")
#engine = create_engine(password) # uncomment when run with docker
connection = engine.connect()
metadata = MetaData()
dwh = Table("weather",metadata,autoload_with=engine)
#stmt = delete(dwh) # uncomment if want to full load
#result = connection.execute(stmt)
#print("Delete successfully")
df.to_sql(
	name='weather',
	con=engine,
	if_exists='append',
	index=False
	)
print("Insert successfully")
