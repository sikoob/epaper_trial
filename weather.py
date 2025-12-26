#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import traceback
import requests

# Automatically add the 'lib' directory relative to the script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(script_dir, 'lib')
sys.path.append(lib_path)
from waveshare_epd import epd7in5_V2

#Base
FONT_DIR = os.path.join(os.path.dirname(__file__), 'font')
PIC_DIR = os.path.join(os.path.dirname(__file__), 'pic')
ICON_DIR = os.path.join(PIC_DIR, 'icon')
refresh_time = 14400

# User defined configuration
header_info = {'X-Api-Key': 'P4WdY9BxfVbvklYzqHZYKQ==RuSCcWKHJY2bRYiQ'} #header info for usage of quote API
QUOTE_BASE_URL = 'https://api.api-ninjas.com/v2/randomquotes'
WEATHER_API_KEY = '32aaf6abc10bd2348865920a6fbd8c23'  # Your API key for openweathermap.com
WEATHER_BASE_URL = f'https://api.openweathermap.org/data/2.5/weather?'
WEATHER_LOCATION = '.Stuttgart'  # Name of location
WEATHER_LATITUDE = '48.782'  # Latitude
WEATHER_LONGITUDE = '9.177'  # Longitude
WEATHER_UNITS = 'metric' # imperial or metric

# Set fonts 
font22 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 22)
font26 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 26)
font30 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 30)
font35 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 35)
font50 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 50)
font60 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 60)
font100 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 100)
font160 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 160)
COLORS = {'black': 'rgb(0,0,0)', 'white': 'rgb(255,255,255)', 'grey': 'rgb(235,235,235)'}

#Initalize E-Paper
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
        
# Fetch quote api
def fetch_quote_data():
    try:
        response = requests.get(QUOTE_BASE_URL, headers=header_info)
        response.raise_for_status()
        logging.info("Quote data fetched successfully.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch Quote data: {e}")
        raise
            
# Process quote data
def process_quote_data(quote_data):
    try:
        quote_info= quote_data[0]
        quote_proc= {
            "quote": quote_info['quote'],
            "author": quote_info['author']
        }
        logging.info("Quote data processed successfully.")
        return quote_proc
    except KeyError as e:
        logging.error(f"Error processing quote data: {e}")
        raise
    
# Fetch weather data
def fetch_weather_data():
    url = f"{WEATHER_BASE_URL}lat={WEATHER_LATITUDE}&lon={WEATHER_LONGITUDE}&units={WEATHER_UNITS}&appid={WEATHER_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info("Weather data fetched successfully.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch weather data: {e}")
        raise
    
# Process weather data
def process_weather_data(weather_data):
    try:
        current = weather_data['main']
        weather_proc = {
            "temp_current": current['temp'],
            "feels_like": current['feels_like'],
            "icon_code": weather_data['weather'][0]['icon']
        }
        logging.info("Weather data processed successfully.")
        return weather_proc
    except KeyError as e:
        logging.error(f"Error processing weather data: {e}")
        raise
        
# Generate display image
def generate_display_image(quote_proc, weather_proc):
    try:
        #Preparation of display
        template = Image.open(os.path.join(PIC_DIR, 'template2.png'))
        draw = ImageDraw.Draw(template)
        icon_path = os.path.join(ICON_DIR, f"{weather_proc['icon_code']}.png")
        icon_image = Image.open(icon_path) if os.path.exists(icon_path) else None
        
        #Display quote and author in top display area
        quote_display = quote_proc['quote']
        
        #Separate quote into different lines with full words once quote is too long
        if len(quote_display) <= 50:
            draw.text((30, 80), f"'{quote_display}'", font=font30, fill=COLORS['black'])
        elif len(quote_display) >50 and len(quote_display) <=100:
            quote_display_separate = quote_display.split()
            quote_splitted_first = ''
            quote_splitted_second = ''
            i = 0
            
            while len(quote_splitted_first) < 50:
                quote_splitted_first = quote_splitted_first + quote_display_separate[i] + ' '
                i= i+1
            
            for item in quote_display_separate[i:]:
                quote_splitted_second = quote_splitted_second + item + ' '
      
            draw.text((30, 80), f"'{quote_splitted_first}", font=font30, fill=COLORS['black'])
            draw.text((30, 120), f"{quote_splitted_second}'", font=font30, fill=COLORS['black'])
        elif len(quote_display) >100 and len(quote_display) <=150:
            quote_display_separate = quote_display.split()
            quote_splitted_first = ''
            quote_splitted_second = ''
            quote_splitted_third = ''
            
            i = 0
            
            while len(quote_splitted_first) < 50:
                quote_splitted_first = quote_splitted_first + quote_display_separate[i] + ' '
                i= i+1
                
            while len(quote_splitted_second) < 50:
                quote_splitted_second = quote_splitted_second + quote_display_separate[i] + ' '
                i= i+1
                
            for item in quote_display_separate[i:]:
                quote_splitted_third = quote_splitted_third + item + ' '
      
            draw.text((30, 80), f"'{quote_splitted_first}", font=font30, fill=COLORS['black'])
            draw.text((30, 120), f"{quote_splitted_second}", font=font30, fill=COLORS['black'])
            draw.text((30, 160), f"{quote_splitted_third}'", font=font30, fill=COLORS['black'])
        else:   #if too many characters, the quote will be shortened
            quote_display_separate = quote_display.split()
            quote_splitted_first = ''
            quote_splitted_second = ''
            quote_splitted_third = ''
            
            i = 0
            
            while len(quote_splitted_first) < 50:
                quote_splitted_first = quote_splitted_first + quote_display_separate[i] + ' '
                i= i+1
                
            while len(quote_splitted_second) < 50:
                quote_splitted_second = quote_splitted_second + quote_display_separate[i] + ' '
                i= i+1
                
            while len(quote_splitted_third) < 47:
                quote_splitted_third = quote_splitted_third + quote_display_separate[i] + ' '
                i= i+1
                
            quote_splitted_third = quote_splitted_third + "...'" #... to show continuance
      
            draw.text((30, 80), f"'{quote_splitted_first}", font=font30, fill=COLORS['black'])
            draw.text((30, 120), f"{quote_splitted_second}", font=font30, fill=COLORS['black'])
            draw.text((30, 160), f"{quote_splitted_third}", font=font30, fill=COLORS['black']) 
            
        draw.text((30, 240), f"- {quote_proc['author']}", font=font22, fill=COLORS['black'])
       
        #Display of weather symbol left bottom
        if icon_image:
            template.paste(icon_image, (65, 310))
        
        #Display of actual and felt temperatur mid bottom
        draw.text((390, 325), f"{weather_proc['temp_current']:.0f}°C", font=font60, fill=COLORS['black'])
        draw.text((345, 410), f"Gefühlt: {weather_proc['feels_like']:.0f}°C", font=font35, fill=COLORS['black'])
        
        #Display of time and date of last update right bottom
        draw.text((627, 330), "UPDATE", font=font35, fill=COLORS['white'])
        current_time = datetime.now().strftime('%H:%M')
        draw.text((627, 375), current_time, font=font50, fill=COLORS['white'])
        current_day = datetime.today().strftime('%d.%m.%Y')
        draw.text((627, 435), current_day, font=font26, fill=COLORS['white'])
        return template
    except Exception as e:
        logging.error(f"Error generating display image: {e}")
        raise

# Display image on screen
def display_image(image):
    try:
        #Create image for setup
        image.save("trial_setup.png")

        #Setting up ePaper
        h_image = Image.new('1', (epd.width, epd.height), 255)
        h_image.paste(image, (0, 0))
        epd.display(epd.getbuffer(h_image))
        logging.info("Image displayed on e-paper successfully.")
    except Exception as e:
        logging.error(f"Failed to display image: {e}")
        raise
        
# Main function
def main():
    try:        
        #Call all necessary functions
        quote_data = fetch_quote_data()
        quote_proc = process_quote_data(quote_data)
        weather_data= fetch_weather_data()
        weather_proc = process_weather_data(weather_data)        
        image = generate_display_image(quote_proc, weather_proc)
        display_image(image)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    #Execute main function every 4 hours after initialization according to set refresh time. Stop function once an error arises
    try:
        running = 0
        while running < 1:
            epd.Clear()             #Clearing ePaper screen every 4 hours
            main()
            time.sleep(refresh_time)
            #running = 1            #can be used to break code for debugging sessions to stop automatic while loop
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}. The process will be stopped until error is resolved.")
        running = 1
        epd.sleep() #turn off ePaper screen
        