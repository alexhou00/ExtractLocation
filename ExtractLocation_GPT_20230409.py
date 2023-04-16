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
prompt = '''以下為部分史記文本，請擷取文本中關於各國相對於某地點的距離與方位資料。並將國名、相對地點、方位、里程設定為欄位，請僅根據文本所提供的資訊製成表格，並保持里程為原文之中文數字：\n（例：若原文為「大宛國東至都護治」，此時國名為大宛國、相對地點為都護治，則方位應為「西」）\n'''

# for paragraph in text.split('\n')[0]:
paragraph = text.split('\n')[0]
msgs = [{"role": "user", "content": prompt + paragraph}]
response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                        max_tokens=1024,
                                        temperature=0.3,
                                        messages=msgs)
print(table := response.choices[0].message.content)
print(f"Usage: {response.usage['total_tokens']} tokens")

