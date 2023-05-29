# -*- coding: utf-8 -*-
"""
Created on Mon May 29 08:11:35 2023

@author: alexh

FAILED?!
"""

from PIL import Image, ImageDraw, ImageFont
import csv
import hashlib

def hashColor(string_to_hash):
    # Define the string to hash and the maximum RGB value
    # string_to_hash = "hello world"
    max_rgb_value = 255
    if string_to_hash != None:
        # Hash the string using SHA-256 and convert the resulting hexadecimal string to an integer
        hashed_string = int(hashlib.sha256(string_to_hash.encode()).hexdigest(), 16)
        
        # Extract the red, green, and blue components from the hashed integer
        red = hashed_string % (max_rgb_value + 1)
        green = (hashed_string // (max_rgb_value + 1)) % (max_rgb_value + 1)
        blue = (hashed_string // ((max_rgb_value + 1) ** 2)) % (max_rgb_value + 1)
        
        # Create an RGB tuple using the extracted color components
        rgb_tuple = (red, green, blue)
        
        return rgb_tuple # Output: (190, 160, 205)
    else:
        return (0,0,0)

# Create a white blank image
width, height = 1500, 900
image = Image.new("RGB", (width, height), "white")

# Create a drawing object
draw = ImageDraw.Draw(image)

# Set the font and font size
font = ImageFont.truetype(r"C:\Windows\Fonts\msjh.ttc", 24)

with open('GPT-4_RGH_numerals.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    sources = []
    for row in reader:
        sources.append(row[4])
        
del sources[0]
sources = list(set(sources))

for i, text in enumerate(sources):
    if text == '--':
        continue
    # Define the text and its position
    text_position = (50, 60+i*50)

    # Define the color block position and size
    block_position = (200, 50+i*50, 300, 100+i*50)

    # Define the color for the block
    block_color = hashColor(text)

    # Draw the text on the image
    draw.text(text_position, text, font=font, fill="black")
    
    # Draw the color block on the image
    draw.rectangle(block_position, fill=block_color)

# Save the image
image.save("plt/legend_RGH.png")