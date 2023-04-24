# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 22:01:42 2023

@author: alexh
"""
# requires python 3.8 or above

# text preprocess (xml -> pure text) => tokenization
# => tag PoS => parse grammar (place is at where)


import logging
import os
import openai

import csv

def chatgpt_to_csv(table, num):
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
    with open('gpt_output.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if num == 0: writer.writerow(headers)
        writer.writerows(data)

# Config the logging module
for name, logger in logging.root.manager.loggerDict.items():
    logger.disabled=True
logging.basicConfig(level=logging.INFO)

openai.api_key = os.environ['openai_api']

# List all books to use
books = ['史記v123', '漢書v96', '後漢書v88']
# Read Original text (text preprocessing, xml -> str)
texts = []
with open(f'文本/{books[0]}.xml', 'r', encoding='utf-8') as f:
    for line in f:
        # remove ascii chars, which means to delete <tags>
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
        if line.endswith('</s>\n'): texts.append('\n')

# each row of text (list) -> combine to string
text = ''.join(texts)

prompt = '''以下為部分史記文本，請擷取文本中關於各地名相對於某個地點的距離與方位資料。並將地名、相對地點、方位、里程設定為欄位，請僅根據文本內容製成表格，並保持里程為原文之中文數字：\n（其中相對地點為「地名」在相對於該「相對地點」的「方位」方向，甲在乙的西方，即「地名」欄位為甲，「相對地點」為乙，「方位」為西）\n'''
prompt = '''
以下為部分史記文本，請擷取文本中關於各國相對於某地點的距離與方位資料。並將國名、相對地點、方位、里程、來源設定為欄位，請僅根據文本所提供的資訊製成表格，並保持里程為原文之中文數字，且切勿亂湊句子，若無合適結果可略過：
'''
# prompt = '''以下為部分史記文本，請擷取文本中關於各國相對於某地點的距離與方位資料。並將國名、相對地點、方位、里程設定為欄位，並補充一欄位為資料來源，製成表格，並保持里程為原文之中文數字：\n'''

with open('gpt_output.csv', mode='w') as file:
    file.truncate(0)

for num, paragraph in enumerate([text.split('\n')[9]]):#enumerate([''.join(text.split('\n')[2:3])]):
    # paragraph = text.split('\n')[0]
    msgs = [{"role": "user", "content": prompt + paragraph}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            max_tokens=2048,
                                            temperature=0.1,
                                            messages=msgs)
    print(table := response.choices[0].message.content)
    print(f"Usage: {response.usage['total_tokens']} tokens")

    chatgpt_to_csv(table, num)
    
        
        

"""       
table = '''國名 | 相對地點 | 方位 | 里程
--- | --- | --- | ---
大宛國 | 長安 | 西 | 萬二千五百五十里
大宛國 | 都護治 | 東 | 不詳
大宛國 | 大月氏 | 西南 | 不詳
大宛國 | 大月氏 | 南 | 不詳
大宛國 | 康居 | 北 | 不詳'''"""


