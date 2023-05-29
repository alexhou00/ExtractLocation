# -*- coding: utf-8 -*-
"""
Created on Mon May 29 07:40:27 2023

@author: alexh

Convert Chinese Numerals to 123 of the GPT-4 generated table (manually to csv)
"""

import csv

from chinese_numerals import chineseNumeralsToInteger as c2i


UNKNOWN_KEYWORDS = ["--", "-", "不詳", "", "無", "未詳", "未提及", "資訊不足", "不明", "未提及", "未嘗見", "未提供", "無資料", '/', "未知"]
UNKNOWN_PREFIXES = ['無具體', '文中未', '文本未']


def is_empty(string):  # Check...
    # if cell == unknown
    # return if is unknown (=empty)
    string = string.strip()
    if string in UNKNOWN_KEYWORDS or any(string.startswith(prefix) for prefix in UNKNOWN_PREFIXES):
        return True
    else:
        return False
    
    
def handle_numerals(row):  # Handle the 里程 column, Chinese to Integers
    if row[3].endswith('里') and '數' not in row[3]:
        if not any(char.isdigit() for char in row[3]): # if has no numerals (not even one 阿拉伯數字)
            row[3] = str(c2i(row[3][:-1])) + '里'  # c2i -> chinese numerals to integer
    return row

def replace_unknown(lst):
    # Replace these unknown text by "--"
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

with open('GPT-4_RGH.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    data = []
    for row in reader:
        # - 目前做法：若方位row[2]、里程row[3]皆空（即不詳或"--"），則於寫入檔案前刪除該列
        # - 若國名 row[0] 或相對地點 row[1] 亦有任一為空，亦刪除該列
        if not (((is_empty(row[2])) and (is_empty(row[3]))) or (is_empty(row[0])) or (is_empty(row[1]))):
            row = handle_numerals(row)
            # writer.writerow()
            data.append(replace_unknown(row))
            
            
with open('GPT-4_RGH_numerals.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)
