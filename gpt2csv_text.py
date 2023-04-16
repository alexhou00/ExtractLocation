# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 22:40:57 2023

@author: alexh
"""

import csv

def chatgpt_to_csv(table):
    # Split the table into rows
    rows = table.strip().split('\n')
    # Split the header row into columns
    headers = rows[0].split(' | ')
    # Create a list to hold the rows of data
    data = []
    # Loop over the remaining rows and split them into columns
    for row in rows[2:]:
        data.append(row.split(' | '))
    # Write the data to a CSV file
    with open('gpt_output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)
        
table = '''國名 | 相對地點 | 方位 | 里程
--- | --- | --- | ---
大宛國 | 長安 | 西 | 萬二千五百五十里
大宛國 | 都護治 | 東 | 不詳
大宛國 | 大月氏 | 西南 | 不詳
大宛國 | 大月氏 | 南 | 不詳
大宛國 | 康居 | 北 | 不詳'''

chatgpt_to_csv(table)