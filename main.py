#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Created on Tue Apr 27 12:09:34 2021
"""
@author: kaustuv
"""
import streamlit as st 
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
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

import ephem
from zoneinfo import ZoneInfo

## Procs
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


format = "%Y-%m-%d %H:%M:%S.%f"
reftime = 1800
if os.path.exists('lastrun.txt'):
    f = open('lastrun.txt','r')
    lastrun = f.read()
    lastrun = datetime.datetime.strptime(lastrun, format).timestamp()
    elapsed = datetime.datetime.now().timestamp() - lastrun
else:
    elapsed = reftime+1

#-----------------------------
# TEMP DIABLE LOGIC
elapsed = reftime-1
#-----------------------------

if elapsed > reftime:

#---------------------------------
# Current Weather Image
#---------------------------------

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
    st.image('04_curweather.jpg')
    
  
    
#-----------------------------------
# Historical Data
#-----------------------------------

df = pd.read_csv('vskpwdata.csv')
df['obsDate'] = pd.to_datetime(df['obsDate'], format = "%d-%m-%y %H:%M")
df = df[-720:]

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

ax[0].legend(loc='upper left')
ax[0].grid()


# Precipitation
x=df['obsDate']
y = np.array(df['RH'])
y2 = np.array(df['rain'].astype(int))
y3 = np.array(df['clouds'].astype(int))

# ax[1].plot(x,y, color='C0', alpha=0.1, label='Relative Humidity')
ax[1].spines.left.set_position(("axes", -0.01))
ax[1].fill_between(x,np.zeros(len(y)),y, color='C0', alpha=0.1, label='Relative Humidity')
ax[1].legend(loc=[0.007,0.90], framealpha=1)
ax[1].set_ylim(bottom=0)
# ax[1].plot(x,y3, color='gray', alpha=0.1, label='cloud Cover')
ax1 = ax[1].twinx()
ax1.spines.right.set_position(("axes", 1.01))
ax1.fill_between(x,np.zeros(len(y3)),y3, color='gray', alpha=0.2, label='cloud Cover')
ax1.legend(loc=[0.007,0.82], framealpha=1)
ax1.set_ylim(bottom=0)
ax2 = ax[1].twinx()
ax2.spines.right.set_position(("axes", 1.08))
ax2.plot(x,y2, color = 'g', label='Precipitation')
ax2.fill_between(x,np.zeros(len(y2)),y2, color='g', alpha=0.5)

ax[1].set(xlabel="Date",
       ylabel="Relative Humidity (%)",
       title="Precipitation")
ax1.set(ylabel="Cloud Cover (%)")
ax2.set(ylabel="Precipitation (mm)")
ax2.legend(loc=[0.007,0.74], framealpha=1)
plim = np.max([4,np.max(y2)])
ax2.set_ylim([0,plim])

ax[1].spines['left'].set_color('C0')
ax1.spines['right'].set_color('gray')
ax2.spines['right'].set_color('g')

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
ax[2].set_ylim([0,45])
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

    
st.image('meteo.jpg')
st.image('windrose.jpg')


#-------------------------------
def plot_object(ax,x,y,txt,color,markersize):
    x1,y1 = x,y
    x2,y2 = markersize/2,markersize/2
    ax.plot(x, y, marker='o', color=color, markersize=markersize, markeredgecolor='k')
    ax.annotate(txt,
                xy=(x1, y1), xycoords='data',
                xytext=(x2, y2), textcoords='offset points',
                )

def plot_moon(ax,x,y,txt,color,markersize):
    x1,y1 = x,y
    x2,y2 = markersize/2,markersize/2
    nnm = ephem.next_new_moon(vsk.date)  
    pnm = ephem.previous_new_moon(vsk.date)  
    lunation = (vsk.date - pnm) / (nnm - pnm)  
    symbol = lunation * 26
    if symbol < 0.2 or symbol > 25.8:
        symbol = '1'
    else:  
        symbol = chr(ord('A') + int(symbol + 0.5) - 1)
    
    prop = FontProperties(fname='moon_phases.ttf', size=markersize)
    ax.text(x,y, symbol, fontproperties=prop)
    ax.annotate(txt,
            xy=(x1, y1), xycoords='data',
            xytext=(x2, y2), textcoords='offset points',
            )   
    
 
# Observer Location
lat = '17.674379'
lon = '83.284501'

# Observer Data
vsk = ephem.Observer()
vsk.lat = lat
vsk.lon = lon
vsk.date = datetime.datetime.utcnow()
tz = 'Asia/Kolkata'
zone = ZoneInfo(tz)

fig, ax = plt.subplots(figsize=[12,12])
ax = plt.subplot(1,1,1, projection='polar')

# Sun
sun = ephem.Sun(vsk)
if np.degrees(sun.alt)>0:
    plot_object(ax, sun.az, np.degrees(sun.alt), '','orange',np.abs(sun.mag-14.7))
    sr = vsk.previous_rising(ephem.Sun())
    sr = ephem.to_timezone(sr, zone)
    ss = vsk.next_setting(ephem.Sun())
    ss = ephem.to_timezone(ss, zone)
    txt = 'Sunrise: '+ datetime.datetime.strftime(sr,'%H:%M')+'\nSunset : '+datetime.datetime.strftime(ss,'%H:%M')
    
    ax.annotate(txt,
                xy=(sun.az, np.degrees(sun.alt)), xycoords='data',
                xytext=(0, -34), textcoords='offset points',
                )
    
moon = ephem.Moon(vsk)
if np.degrees(moon.alt)>0:
    plot_moon(ax, moon.az, np.degrees(moon.alt), '',(moon.moon_phase,moon.moon_phase,moon.moon_phase),np.abs(moon.mag-14.7))
    mr = vsk.previous_rising(ephem.Moon())
    mr = ephem.to_timezone(mr, zone)
    ms = vsk.next_setting(ephem.Moon())
    ms = ephem.to_timezone(ms, zone)
    mp = moon.moon_phase
    fm = ephem.next_full_moon(vsk.date)
    fm = ephem.to_timezone(fm, zone)
    nm = ephem.next_new_moon(vsk.date)
    nm = ephem.to_timezone(nm, zone)

    txt = 'Moonrise: '+ datetime.datetime.strftime(mr,'%H:%M')+'\nMoonset : ' + \
            datetime.datetime.strftime(ms,'%H:%M') + \
            '\nMoon Phase: '+str(int(mp*100))+'%' + \
            '\nNext Full Moon: '+ datetime.datetime.strftime(fm,'%d-%b-%y %H:%M') + \
            '\nNextNew Moon: '+ datetime.datetime.strftime(nm,'%d-%b-%y %H:%M')
    
    ax.annotate(txt,
                xy=(moon.az, np.degrees(moon.alt)), xycoords='data',
                xytext=(0, 30), textcoords='offset points',
                )
    
mer = ephem.Mercury(vsk)
if np.degrees(mer.alt)>0:
    plot_object(ax, mer.az, np.degrees(mer.alt), mer.name,'k',np.abs(mer.mag-14.7))
    
ven = ephem.Venus(vsk)
if np.degrees(ven.alt)>0:
    plot_object(ax, ven.az, np.degrees(ven.alt), ven.name,'k', np.abs(ven.mag-14.7))
    
mar = ephem.Mars(vsk)
if np.degrees(mar.alt)>0:
    plot_object(ax, mar.az, np.degrees(mar.alt), mar.name,'k',np.abs(mar.mag-14.7))
    
jup = ephem.Jupiter(vsk)
if np.degrees(jup.alt)>0:
    plot_object(ax, jup.az, np.degrees(jup.alt), jup.name,'k',np.abs(jup.mag-14.7))
    
sat = ephem.Saturn(vsk)
if np.degrees(sat.alt)>0:
    plot_object(ax, sat.az, np.degrees(sat.alt), sat.name,'k',np.abs(sat.mag-14.7))

ura = ephem.Uranus(vsk)
if np.degrees(ura.alt)>0:
    plot_object(ax, ura.az, np.degrees(ura.alt), ura.name,'k',np.abs(ura.mag-14.7))
    
nep = ephem.Neptune(vsk)
if np.degrees(nep.alt)>0:
    plot_object(ax, nep.az, np.degrees(nep.alt), nep.name,'k',np.abs(nep.mag-14.7))

plu = ephem.Pluto(vsk)
if np.degrees(plu.alt)>0:
    plot_object(ax, plu.az, np.degrees(plu.alt), plu.name,'k',np.abs(plu.mag-14.7))
    
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_rmax(90)

ax.set_rlim(bottom=90, top=0)
# ax.set_xticklabels(['N','NE','E','SE','S','SW','W','NW'])
ax.set_title('Sky Map')
plt.savefig('skymap.jpg')
st.image('skymap.jpg')
