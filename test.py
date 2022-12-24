import streamlit as st

"""
## Web scraping on Streamlit Cloud with Selenium
[![Source](https://img.shields.io/badge/View-Source-<COLOR>.svg)](https://github.com/snehankekre/streamlit-selenium-chrome/)
This is a minimal, reproducible example of how to scrape the web with Selenium and Chrome on Streamlit's Community Cloud.
Fork this repo, and edit `/streamlit_app.py` to customize this app to your heart's desire. :heart:
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# @st.experimental_singleton
# def get_driver():


options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--headless')
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = get_driver()
browser.get("https://openweathermap.org/weathermap?basemap=map&cities=false&layer=clouds&lat=17.69&lon=83.2093&zoom=8")
# print(driver.page_source)
timeout = 15

url = 'https://openweathermap.org/weathermap?basemap=map&cities=false&layer=clouds&lat=17.69&lon=83.2093&zoom=8'
Xpath = '//*[@id="map"]/div[1]/div[1]/div[2]/div[2]/*'

browser.get(url)
# element_present = EC.visibility_of_all_elements_located((By.XPATH, Xpath))
# ImageList = WebDriverWait(browser, timeout).until(element_present)

# s = []
# l = []
# t = []
# for element in ImageList:

#     src = element.get_attribute('src')
#     data = element.get_attribute('style')
#     # print(data)
#     img_data = parseData(data)
#     l.append(img_data[2])
#     t.append(img_data[3])
#     s.append(src)
#     h = img_data[0]
#     w = img_data[1]
# st.text(h,w)
# Footer
# © 2022 GitHub, Inc.
# Footer navigation
# Terms
# Privacy
