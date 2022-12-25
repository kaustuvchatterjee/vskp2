#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Created on Tue Apr 27 12:09:34 2021
"""
@author: kaustuv
"""
import streamlit as st 
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import urllib.request
# import numpy as np
# import matplotlib.pyplot as plt

import requests, datetime
import os

import matplotlib.dates as mdates
# from matplotlib.dates import DateFormatter
import pandas as pd
from windrose import WindroseAxes

format = "%Y-%m-%d %H:%M:%S.%f"
reftime = 1800
if os.path.exists('lastrun.txt'):
    f = open('lastrun.txt','r')
    lastrun = f.read()
    lastrun = datetime.datetime.strptime(lastrun, format).timestamp()
    elapsed = datetime.datetime.now().timestamp() - lastrun
else:
    elapsed = reftime+1
    
if elapsed > reftime:
#---------------------------------
# Current Weather Image
#-------------------------------------

    def parseData(data):
    
        attrList = data.split(';')
        h = attrList[0]
        h = h.split(':')[1].strip()
        h = int(h.split('px')[0].strip())
    
        w = attrList[1]
        w = w.split(':')[1].strip()
        w = int(w.split('px')[0].strip())
    
        l = attrList[2]
        l = l.split(':')[1].strip()
        l = int(l.split('px')[0].strip())
    
        t = attrList[3]
        t = t.split(':')[1].strip()
        t = int(t.split('px')[0].strip())
    
        return [h,w,l,t]
    
    def createBaseFromTiles(s, l, t, h, w):
        # print(s,l,t)
        # min_l = np.min(l)
        max_l = np.max(l)+w
        # min_t = np.min(t)
        max_t = np.max(t)+h
        img = Image.new('RGBA',(max_l, max_t))
        # print(min_l, max_l, min_t, max_t)
    
        
        for i in range(len(s)):
            
            urllib.request.urlretrieve(s[i], 'tmp.png')
            fmg = Image.open('tmp.png')
            # fmg.resize((w,h))
            img.paste(fmg,(l[i],t[i]))
            # img.show()
        img = img.convert('RGB')
        
        t=3
        width = img.size[0] 
        height = img.size[1] 
        for i in range(0,width):# process all pixels
            for j in range(0,height):
                data = img.getpixel((i,j))
                #print(data) #(255, 255, 255)
                if ((data[0]>=211-t and data[0]<=211+t) and (data[1]>=217-t and data[1]<=217+t) and (data[2]>=220-t and data[2]<=220+t)):
                    img.putpixel((i,j),(data[0],data[1],255))
        
        return img
    
    def pasteCloudLayer(img, s,l,t,h,w):
        for i in range(len(s)):
            
            urllib.request.urlretrieve(s[i], 'tmp.png')
            fmg = Image.open('tmp.png')
            # fmg.resize((w,h))
            img.paste(fmg,(l[i],t[i]),fmg)
    
        img = img.convert('RGB')    
        return img
    
    def pasteRadarLayer(img, s,l,t,h,w):
        for i in range(len(s)):
            
            urllib.request.urlretrieve(s[i], 'tmp.png')
            fmg = Image.open('tmp.png')
            fmg = fmg.resize((512,512))
            # fmg.save('radar/'+str(i)+'.png')
            img.paste(fmg,(l[i],t[i]),fmg)
            # img.save('radar/'+str(i)+'_c.png')
            
        img = img.convert('RGB')    
        return img
    
    def windDirImg(wind_dir):
        fig=plt.figure(figsize=(1,1))
        ax=fig.add_axes([0.1, 0.1, 0.8, 0.8],polar=True)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_rmax(90)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.arrow(np.radians(wind_dir),np.radians(wind_dir),0,0)
        plt.savefig('wind_dir.png', transparent=True)
        wind_dir_img = Image.open('wind_dir.png')
        return wind_dir_img
    
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument("--headless")
    options.add_argument("window-size=1920,1080")
    timeout = 15
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    
    # Base Map
    if os.path.exists('01_base.jpg'):
        img = Image.open('01_base.jpg')
    else:
        url = 'https://openweathermap.org/weathermap?basemap=map&cities=false&layer=clouds&lat=17.69&lon=83.2093&zoom=8'
        Xpath = '//*[@id="map"]/div[1]/div[1]/div[2]/div[2]/*'
    
        browser.get(url)
#         element_present = EC.visibility_of_all_elements_located((By.XPATH, Xpath))
#         ImageList = WebDriverWait(browser, timeout).until(element_present)
    
        s = []
        l = []
        t = []
        for element in ImageList:
    
            src = element.get_attribute('src')
            data = element.get_attribute('style')
            # print(data)
            img_data = parseData(data)
            l.append(img_data[2])
            t.append(img_data[3])
            s.append(src)
            h = img_data[0]
            w = img_data[1]
    
        img = createBaseFromTiles(s,l,t,h,w)
        img.save('01_base.jpg')
        
    print('Base layer created!')
    
    
    # Add Cloud layer
    url = 'https://openweathermap.org/weathermap?basemap=map&cities=false&layer=clouds&lat=17.69&lon=83.2093&zoom=8'
    Xpath = "//*[@id='map']/div[1]/div[1]/div[1]/div[2]/*"
    
    browser.get(url)
    element_present = EC.visibility_of_all_elements_located((By.XPATH, Xpath))
    ImageList = WebDriverWait(browser, timeout).until(element_present)
    
    s = []
    l = []
    t = []
    for element in ImageList:
    
        src = element.get_attribute('src')
        data = element.get_attribute('style')
        # print(data)
        img_data = parseData(data)
        l.append(img_data[2])
        t.append(img_data[3])
        s.append(src)
        h = img_data[0]
        w = img_data[1]
    
    cloud_img = pasteCloudLayer(img,s,l,t,h,w)
    cloud_img.save('02_clouds.jpg')
    print('Cloud layer created!')
    
    # Add Radar layer
    url = 'https://openweathermap.org/weathermap?basemap=map&cities=false&layer=radar&lat=17.69&lon=83.2093&zoom=8'
    Xpath = "//*[@id='map']/div[1]/div[1]/div[1]/div[2]/*"
    
    browser.get(url)
    element_present = EC.visibility_of_all_elements_located((By.XPATH, Xpath))
    ImageList = WebDriverWait(browser, timeout).until(element_present)
    
    s = []
    l = []
    t = []
    for element in ImageList:
    
        src = element.get_attribute('src')
        data = element.get_attribute('style')
        # print(data)
        img_data = parseData(data)
        l.append(img_data[2])
        t.append(img_data[3])
        s.append(src)
        h = img_data[0]
        w = img_data[1]
    
    radar_img = pasteRadarLayer(cloud_img,s,l,t,h,w)
    radar_img.save('03_radar.jpg')
    print('Radar layer created!')
    
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
    
    temp = ''
    RH = ''
    mslp = ''
    wind_speed = ''
    wind_dir = ''
    clouds = ''
    w_desc = ''
    rain = ''
    pop=''
    
    
    
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
        w_icon = "https://openweathermap.org/img/wn/"+z[0]["icon"]+"@2x.png"
        urllib.request.urlretrieve(w_icon, 'wimg.png')
        wicon = Image.open('wimg.png')
        
        a = x["wind"]
        wind_speed = a["speed"]
        wind_speed = np.round(wind_speed*3.6,1)
        wind_dir = a["deg"]
        wind_dir_img = windDirImg(wind_dir)
        clouds = x["clouds"]["all"]
        sunrise = int(x["sys"]["sunrise"])+int(x["timezone"])
        sunrise = datetime.datetime.utcfromtimestamp(int(sunrise)).strftime('%H:%M')
        sunset = int(x["sys"]["sunset"])+int(x["timezone"])
        sunset = datetime.datetime.utcfromtimestamp(int(sunset)).strftime('%H:%M')
        dt = datetime.datetime.utcfromtimestamp(int(x["dt"]+int(x["timezone"]))).strftime('%d-%m-%y %H:%M')
        if rain in x:
            rain = x['rain']['ih']
        else:
            rain = '0'
        # try:
        #     rain = x['rain']['ih']
        # except:
        #     rain = '0'
        pop = int(f["list"][0]['pop']*100)
    
    # Embed  in Image
    font_size = 28
    # yp = 60
    font = ImageFont.truetype("OpenSans-Regular.ttf", font_size)
    # img = radar_img.copy()
    img = Image.open('03_radar.jpg')
    img.paste(wicon, (0,14), wicon)
    img.paste(wind_dir_img, (10,164), wind_dir_img)
    draw = ImageDraw.Draw(img)
    
    tmstr = 'Visakhapatnam - '+str(dt)
    tmstr = tmstr+'\n'+str(w_desc).upper()
    tmstr = tmstr+'\nTemp:                  '+str(temp)+'°C'
    tmstr = tmstr+'\nFeels Like:           '+str(tempF)+'°C'
    tmstr = tmstr+'\nRH:                       '+str(RH)+'%'
    tmstr = tmstr+'\nWind:                   '+str(wind_speed)+' km/h from '+str(wind_dir)+'°'
    tmstr = tmstr+'\nMSLP:                  '+str(mslp)+' hPa'
    tmstr = tmstr+'\nCloud Cover:      '+str(clouds)+'%'
    tmstr = tmstr+'\nRain (1h):             '+str(rain)+' mm'
    tmstr = tmstr+'\nChance of rain:   '+str(pop)+'%'
    tmstr = tmstr+'\nSunrise:               '+str(sunrise)
    tmstr = tmstr+'\nSunset:                '+str(sunset)
    
    draw.text((120, 10),tmstr,(0,0,0),font=font)
    
    img.save('04_curweather.jpg')
    
  
    
    #-----------------------------------
    # Historical Data
    #-----------------------------------
    
    df = pd.read_csv('https://raw.githubusercontent.com/kaustuvchatterjee/vskp2/main/vskpwdata.csv')
    df['obsDate'] = pd.to_datetime(df['obsDate'])
    
    fig2, ax = plt.subplots(3,1, figsize=(12,12), sharex=True)
    
    # Temperature
    x=df['obsDate']
    y = df['temp']
    y2 = df['tempFeel']
    
    ax[0].plot(x,y, color='C0', label='Temperature')
    ax[0].plot(x,y2, color = 'C1', label='Feels Like')
    
    ax[0].set(xlabel="Date",
           ylabel="Temp (°C)",
           title="Temperature")
    ax[0].set_ylim([0,50])
    
    ax[0].legend()
    ax[0].grid()
    
    
    # Precipitation
    x=df['obsDate']
    y = np.array(df['RH'])
    y2 = np.array(df['rain'].astype(int))
    y3 = np.array(df['clouds'].astype(int))
    
    ax[1].plot(x,y, color='C0', label='Relative Humidity')
    ax[1].fill_between(x,np.zeros(len(y)),y, color='C0', alpha=0.01)
    ax[1].plot(x,y3, color='gray', label='cloud Cover')
    ax[1].fill_between(x,np.zeros(len(y3)),y3, color='gray', alpha=0.1)
    ax[1].legend(loc=2, frameon=False)
    ax[1].set_ylim(bottom=0)
    ax2 = ax[1].twinx()
    ax2.plot(x,y2, color = 'g', label='Rain')
    ax2.fill_between(x,np.zeros(len(y2)),y2, color='g', alpha=0.5)
    
    ax[1].set(xlabel="Date",
           ylabel="Relative Humidity (%)",
           title="Precipitation")
    ax2.set(ylabel="Precipitation (mm)")
    ax2.legend(loc=[0.007,0.76], frameon=False)
    ax2.set_ylim(bottom=0)
    
    ax[1].grid()
    
    # Wind
    ws = df['windSpeed']
    wd = df['windDir']
    
    wd = 270-wd
    x=df['obsDate']
    y = ws
    u = np.cos(np.radians(wd))
    v = np.sin(np.radians(wd))
    
    ax[2].plot(x,y, color='C0')
    ax[2].quiver(x,y,u,v, color='#008080', width=0.005, pivot='mid', scale=5, scale_units='inches')
    
    ax[2].set(xlabel="Date",
           ylabel="Wind Speed (km/h)",
           title="Wind")
    ax[2].set_ylim([0,30])
    locator = mdates.AutoDateLocator(minticks=3, maxticks=12)
    formatter = mdates.ConciseDateFormatter(locator)
    formatter.formats = ['%y',  # ticks are mostly years
                         '%b',       # ticks are mostly months
                         '%d',       # ticks are mostly days
                         '%H:%M',    # hrs
                         '%H:%M',    # min
                         '%S.%f', ]  # secs
    # these are mostly just the level above...
    formatter.zero_formats = [''] + formatter.formats[:-1]
    # ...except for ticks that are mostly hours, then it is nice to have
    # month-day:
    formatter.zero_formats[3] = '%d-%b'
    
    formatter.offset_formats = ['',
                                '%Y',
                                '%b %Y',
                                '%d %b %Y',
                                '%d %b %Y',
                                '%d %b %Y %H:%M', ]
    
    ax[2].xaxis.set_major_locator(locator)
    ax[2].xaxis.set_major_formatter(formatter)
    ax[2].grid()
    
    fig2.tight_layout()
    plt.savefig('meteo.jpg',dpi=150)

    
    
    ax = WindroseAxes.from_ax()
    ax.bar(df['windDir'], df['windSpeed'], normed=True, opening=0.8, edgecolor='white',bins=np.arange(0, 20, 4))
    ax.set_legend(loc=[0.9,0.9], frameon=False)
    ax.set(title="Windrose\nWind Speed (km/h)",
          yticklabels=[])
    fig3 = plt.gcf()
    plt.savefig('windrose.jpg')

    f = open('lastrun.txt','w+')
    f.write(str(datetime.datetime.now()))
    f.close()

    
st.image('04_curweather.jpg')
st.image('meteo.jpg')
st.image('windrose.jpg')
