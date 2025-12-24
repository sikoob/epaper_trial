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
header_info = {'X-Api-Key': 'P4WdY9BxfVbvklYzqHZYKQ==RuSCcWKHJY2bRYiQ'}
QUOTE_BASE_URL = 'https://api.api-ninjas.com/v2/randomquotes'


# Set fonts 
font22 = ImageFont.truetype(os.path.join(FONT_DIR, 'Font.ttc'), 22)
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
def process_quote_data(data):
    try:
        quote_info= data[0]
        quote_data= {
            "quote": quote_info['quote'],
            "author": quote_info['author']
        }
        logging.info("Quote data processed successfully.")
        return quote_data
    except KeyError as e:
        logging.error(f"Error processing quote data: {e}")
        raise
        
# Generate display image
def generate_display_image(quote_data):
    try:
        template = Image.open(os.path.join(PIC_DIR, 'template.png'))
        draw = ImageDraw.Draw(template)
        draw.text((30, 200), f"'{quote_data['quote']}'", font=font30, fill=COLORS['black'])
        draw.text((30, 240), f"- {quote_data['author']}", font=font22, fill=COLORS['black'])
        current_time = datetime.now().strftime('%H:%M')
        draw.text((627, 375), current_time, font=font60, fill=COLORS['white'])
        return template
    except Exception as e:
        logging.error(f"Error generating display image: {e}")
        raise

# Display image on screen
def display_image(image):
    try:
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
        data = fetch_quote_data()
        quote_data = process_quote_data(data)
        image = generate_display_image(quote_data)
        display_image(image)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
    
    # Drawing on the Vertical image
    #logging.info("2.Drawing on the Vertical image...")
    #Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #draw = ImageDraw.Draw(Limage)
    #draw.text((2, 0), 'hello world', font = font18, fill = 0)
    #epd.display(epd.getbuffer(Limage))
    #time.sleep(2)
    
    #logging.info("3.read bmp file")
    #Himage = Image.open(os.path.join(picdir, '7in5.bmp'))
    #epd.display(epd.getbuffer(Himage))
    #time.sleep(2)
    
    #logging.info("4.read bmp file on window")
    #Himage2 = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    #bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    #Himage2.paste(bmp, (50,10))
    #epd.display(epd.getbuffer(Himage2))
    #time.sleep(2)

    #logging.info("Clear...")
    #epd.init()
    #epd.Clear()
    
    #logging.info("Goto Sleep...")
    #epd.sleep()
