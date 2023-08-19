import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import requests
import os
import datetime

df = pd.read_csv('vskpwdata.csv')
lasthr = pd.to_datetime(df['obsDate'].iloc[-1], format='%d-%m-%y %H:%M').hour


api_key = "85d5db5a1265e695a3d4b99399f27d57"
base_url1 = "http://api.openweathermap.org/data/2.5/weather?"
base_url2 = "http://api.openweathermap.org/data/2.5/forecast?"
city_name = "Visakhapatnam, IN"

complete_url = base_url1 + "appid=" + api_key + "&q=" + city_name
response = requests.get(complete_url)
x = response.json()
complete_url = base_url2 + "appid=" + api_key + "&q=" + city_name
response = requests.get(complete_url)
f = response.json()

if x["cod"] != "404":


    y = x["main"]
    temp = y["temp"]
    temp = np.round(temp-273.15,1)
    tempF = y["feels_like"]
    tempF = np.round(tempF-273.15,1)
    minTemp = np.round((y["temp_min"]-273.15),0)
    maxTemp = np.round((y["temp_max"]-273.15),0)

    mslp = y["pressure"]
    RH = y["humidity"]

    z = x["weather"]
    w_desc = z[0]["description"]
    # w_icon = "https://openweathermap.org/img/wn/"+z[0]["icon"]+"@2x.png"
    # urllib.request.urlretrieve(w_icon, 'wimg.png')
    # wicon = Image.open('wimg.png')

    a = x["wind"]
    wind_speed = a["speed"]
    wind_speed = np.round(wind_speed*3.6,1)
    wind_dir = a["deg"]
    # wind_dir_img = windDirImg(wind_dir)
    clouds = x["clouds"]["all"]
    # sunrise = int(x["sys"]["sunrise"])+int(x["timezone"])
    # sunrise = datetime.datetime.utcfromtimestamp(int(sunrise)).strftime('%H:%M')
    # sunset = int(x["sys"]["sunset"])+int(x["timezone"])
    # sunset = datetime.datetime.utcfromtimestamp(int(sunset)).strftime('%H:%M')
    dt = datetime.datetime.utcfromtimestamp(int(x["dt"]+int(x["timezone"]))).strftime('%d-%m-%y %H:%M')
    if 'rain' in x:
        rain = x['rain']['1h']
    else:
        rain = 0.0

    # pop = int(f["list"][0]['pop']*100)

# print([dt,temp,tempF,RH,mslp,wind_speed,wind_dir,clouds,rain])
if pd.to_datetime(dt).hour != lasthr:
    y = {'obsDate':[dt],'temp':[temp],'tempFeel':[tempF],'RH':[RH],'MSLP':[mslp],'windSpeed':[wind_speed],'windDir':[wind_dir],'clouds':[clouds],'rain':[rain]}
    df1 = pd.DataFrame(data=y, index=[0])
    df = pd.concat([df, df1], ignore_index=True)
    # df = df.append({'obsDate':dt,'temp':temp,'tempFeel':tempF,'RH':RH,'MSLP':mslp,'windSpeed':wind_speed,'windDir':wind_dir,'clouds':clouds,'rain':rain}, ignore_index=True)
    df.to_csv('vskpwdata.csv', index=False)
