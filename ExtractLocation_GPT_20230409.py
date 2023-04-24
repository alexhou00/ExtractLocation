# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 22:01:42 2023

@author: alexh
"""
# requires python 3.8 or above

# set to prevent duplicates
# chinese to integer
# InvalidRequestError


import logging
import os
import openai
from openai.error import InvalidRequestError

from chinese_numerals import chineseNumeralsToInteger as c2i


import csv

UNKNOWN_KEYWORDS = ["--", "-", "不詳", "", "無", "未提及", "不明", "未提及", "未嘗見", "未提供", "無資料", '/', "未知"]
UNKNOWN_PREFIXES = ['無具體', '文中未', '文本未']


def is_empty(string):
    # if cell == unknown
    # return if is unknown (=empty)
    string = string.strip()
    if string in UNKNOWN_KEYWORDS or any(string.startswith(prefix) for prefix in UNKNOWN_PREFIXES):
        return True
    else:
        return False

def keep_nonascii_chars(string):
    return ''.join(c for c in string if ord(c) > 127)

def replace_unknown(lst):
    # replace these unknown text by "--"
    for i in range(len(lst)):
        lst[i] = lst[i].strip() # get rid of extra spaces
        if lst[i] in UNKNOWN_KEYWORDS:
            lst[i] = "--"
        if any(lst[i].startswith(prefix) for prefix in UNKNOWN_PREFIXES):  # 無具體xx（e.g., 無具體里程、無具體方位...）
            lst[i] = "--"
        lst[i] = lst[i].strip("| ")  # first or last column: "| 文字" or "文字 |"
    #if len(lst) > 5: lst = lst[:5]  # prevent extra column
    if len(lst[4]) > 20: lst[4] == "--"  # if 來源 too long (which means it is giving whole source sentence)
    return lst

def split_text(text): # split text in half
    # Split the text into sentences
    sentences = text.split('. ')
    # Find the index of the sentence closest to the center of the text
    mid_index = len(sentences)//2
    min_distance = abs(len(text)/2 - len(sentences[mid_index])/2)
    for i, sentence in enumerate(sentences):
        distance = abs(len(text)/2 - len(sentence)/2)
        if distance < min_distance:
            mid_index = i
            min_distance = distance
    # Join the first half of the sentences
    first_half = '. '.join(sentences[:mid_index+1])
    # Join the second half of the sentences
    second_half = '. '.join(sentences[mid_index+1:])
    # Combine the halves and return them
    return first_half, second_half

def custom_split(string):
    # Split a string into a list, but join short elements to the next one.
    result = []
    current = ''
    for part in string.split('\n'):
        current += '\n' + part
        if len(part) > 150:  # if only length larger than 150 then append
            result.append(current.strip())
            current = ''
    if current:
        result.append(current.strip())
    return result

def handle_numerals(row):
    if row[3].endswith('里'):
        if not any(char.isdigit() for char in row[3]): # if has no numerals (not even one 阿拉伯數字)
            row[3] = str(c2i(row[3][:-1])) + '里'  # c2i -> chinese numerals to integer
    return row

def chatgpt_to_csv(table, num):
    if ('|' in table): # standard chatgpt-style format
        # Split the table into rows
        rows = table.strip().split('\n')
        # Split the header row into columns
        headers = rows[0].split(' | ')
        # Create a list to hold the rows of data
        data = []
        # Loop over the remaining rows and split them into columns
        for row in rows[2:]:
            data.append(row.split(' | '))
    else: # space-delimited table (sometimes it just happens)
        # Split the string into lines, and remove any leading or trailing whitespace
        lines = [line.strip() for line in table.split('\n')] 
        # Split each line into cells, using whitespace as the delimiter
        data = [line.split() for line in lines]
        headers, data = data[0], data[2:]
    # Write the data to a CSV file
    with open('gpt_output.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if num == 0: writer.writerow(headers) # if writing the first time then write header
        for row in data:
            # - 目前做法：若方位row[2]、里位row[3]皆空（即不詳或"--"），則於寫入檔案前刪除該列
            # - 若國名 row[0] 或相對地點 row[1] 亦有任一為空，亦刪除該列
            if not (((is_empty(row[2])) and (is_empty(row[3]))) or (is_empty(row[0])) or (is_empty(row[1]))):
                row = handle_numerals(row)
                writer.writerow(replace_unknown(row))

# Config the logging module
for name, logger in logging.root.manager.loggerDict.items():
    logger.disabled=True
logging.basicConfig(level=logging.INFO)

# set openai api key
# enter this line of code before running this script:
# import os;os.environ['openai_api']='yOuR-ApI_KeyHeRE142857'
openai.api_key = os.environ['openai_api']

# List all books to use
books = ['史記v123', '漢書v96', '後漢書v88']
# Read Original text (text preprocessing, xml -> str)
book = books[0]
texts = []
with open(f'文本/{book}.xml', 'r', encoding='utf-8') as f:
    for line in f:
        # remove ascii chars, which means to delete <tags>
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
        if line.endswith('</s>\n'): texts.append('\n')

# each row of text (list) -> combine to string
text = ''.join(texts)

prompt = '''以下為部分史記文本，請擷取文本中關於各地名相對於某個地點的距離與方位資料。並將地名、相對地點、方位、里程設定為欄位，請僅根據文本內容製成表格，並保持里程為原文之中文數字：\n（其中相對地點為「地名」在相對於該「相對地點」的「方位」方向，甲在乙的西方，即「地名」欄位為甲，「相對地點」為乙，「方位」為西）\n'''
prompt = f'''
以下為部分{keep_nonascii_chars(book)}文本，請擷取文本中關於各國相對於某地點的距離與方位資料。並將國名、相對地點、方位、里程、來源設定為欄位，請僅根據文本所提供的資訊製成表格，並保持里程為原文之中文數字，且切勿亂湊句子，若無合適結果可略過：
'''
# prompt = '''以下為部分史記文本，請擷取文本中關於各國相對於某地點的距離與方位資料。並將國名、相對地點、方位、里程設定為欄位，並補充一欄位為資料來源，製成表格，並保持里程為原文之中文數字：\n'''

# clear csv file
with open('gpt_output.csv', mode='w') as file:
    file.truncate(0)

# loop every paragraph
for num, paragraph in enumerate(custom_split(text)): # enumerate([''.join(text.split('\n')[0:2])]): #enumerate([text.split('\n')[3]]):#
    # paragraph = text.split('\n')[0]
    
    msgs = [{"role": "user", "content": prompt + paragraph}]

    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                max_tokens=2048,
                                                temperature=0.1,
                                                messages=msgs)
        
        print(table := response.choices[0].message.content)  # assign the table to variable and print it
        print(f"Usage: {response.usage['total_tokens']} tokens")  # print token usage
        
        try:
            chatgpt_to_csv(table, num)  # write the output to csv table, num is the # of loop
        except IndexError as e:  # perhaps that paragraph does not contain any location info
            print(e)  # so the output (completion) won't be in the chatgpt-style table format
            # and that's why there is the error of list index out of range

    except InvalidRequestError as e: # This model's maximum context length is 4097 tokens. However, you requested too many tokens
        print(e, "split in half")
        paragraphs = split_text(paragraph)
        
        for paragraph_i in paragraphs:
            msgs = [{"role": "user", "content": prompt + paragraph_i}]
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    max_tokens=2048,
                                                    temperature=0.1,
                                                    messages=msgs)
            
            print(table := response.choices[0].message.content)  # assign the table to variable and print it
            print(f"Usage: {response.usage['total_tokens']} tokens")  # print token usage
            
            try:
                chatgpt_to_csv(table, num)  # write the output to csv table, num is the # of loop
            except IndexError as e:  # perhaps that paragraph does not contain any location info
                print(e)  # so the output (completion) won't be in the chatgpt-style table format
                # and that's why there is the error of list index out of range

    
    
        
        

"""       
table = '''國名 | 相對地點 | 方位 | 里程
--- | --- | --- | ---
大宛國 | 長安 | 西 | 萬二千五百五十里
大宛國 | 都護治 | 東 | 不詳
大宛國 | 大月氏 | 西南 | 不詳
大宛國 | 大月氏 | 南 | 不詳
大宛國 | 康居 | 北 | 不詳'''"""


