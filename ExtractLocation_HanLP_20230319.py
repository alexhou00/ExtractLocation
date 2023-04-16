# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 23:46:17 2023


example_text = '''居匈奴中，益寬，騫因與其屬亡鄉月氏，西走數十日至大宛。大宛聞漢之饒財，欲通不
得，見騫，喜，問曰：「若欲何之？」騫曰：「為漢使月氏，而為匈奴所閉道。今亡，唯王使人
導送我。誠得至，反漢，漢之賂遺王財物不可勝言。」大宛以為然，遣騫，'''

Available Tokenization / Chinese NLP modules:
    Jiayan: https://github.com/jiaeyan/Jiayan
    Jieba: https://github.com/fxsjy/jieba
    Stanza: https://github.com/stanfordnlp/stanza
    HanLP: https://github.com/hankcs/HanLP
# tokenization = split words
康居國在京西一萬六百里。其西北可二千里有奄蔡，酒國也。
"""
# text preprocess (xml -> pure text) => tokenization
# => tag PoS => parse grammar (place is at where)

from hanlp_restful import HanLPClient  # HanLP beginner module
from typing import NamedTuple  # c-like struct works like a tuple
from nltk import RegexpParser, Tree
from itertools import groupby

# from urllib.error import HTTPError

from chinese_numerals import chineseNumeralsToInteger, map_nums

import logging

import json
import csv

import os


# Currently not used
class Word(NamedTuple):
    tok: str  # Tokenization
    pos: str  # Part of Speech
    sdp: list  # Semantic Dependency Parsing, 語義依存分析
    ner: list = ['',0,0] # Named Entity Recognition, 命名實體識別

# Config the logging module
for name, logger in logging.root.manager.loggerDict.items():
    logger.disabled=True
logging.basicConfig(level=logging.INFO)

# List all books to use
books = ['史記v123', '漢書v96', '後漢書v88']
# Read Original text (text preprocessing, xml -> str)
texts = []
with open(f'文本/{books[1]}.xml', 'r', encoding='utf-8') as f:
    for line in f:
        # remove ascii chars, which means to delete <tags>
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
        if line.endswith('</s>\n'): texts.append('\n')

# each row of text (list) -> combine to string
text = ''.join(texts)
text = text.split('\n')
text = ''.join(text[:len(text)//2])

# Fill in auth (auth=None -> anonymous), set language='zh' to use Chinese models
HanLP = HanLPClient('https://www.hanlp.com/api', auth=os.environ['API_KEY'], language='zh')

# Use tasks=[...] to run selected tasks only
# type(t) = Document()  # (Document object of hanlp_common.document)
# text = '大宛在匈奴西南，在漢正西，去漢可萬里。其俗土著，耕田，田稻麥。有蒲陶酒。'
t = HanLP(text, tasks=['pos', 'ner', 'sdp'])

# Predefine Known 地名 so we can tag them as LOC directly
# (^To do)
LOCATIONS = ['烏孫', '大夏']

# HanLP results to JSON (readable structure)
json_t = json.loads(str(t)) # type: dict
logging.debug(str(t))

# look for the machine-labeled PoS in those files
filecsv = open('test_hanlp_findloc.csv', 'a', encoding='utf-8', newline='')
filetxt = open('test_hanlp_findloc.txt', 'a', encoding='utf-8')
writer = csv.writer(filecsv)
# text = 'my text to search'
# [list(zip(sentences[0],sentences[1])) for sentences in sentences_t if text in ''.join(sentences[0])]

#   P: Preposition
# LOC: NR && Location (Target Location Names)
#  NR: Proper Nouns
# CNTRY: 「國」
#  AD: ADVerb
#  VV: Normal Verbs
#  LC: Directions of locations (North, east, etc)
#   M: 量詞
#  CD: 數詞
#  PN: 代名詞
#  PU: 標點符號
loc_grammar = "DIS: {<P>?<LOC|NR>+<CNTRY>?<AD>?<VV|P><P>?<LOC|NR>+<AD>?<VV>?(<LC><VV>?<CD>+<M>|<LC>|<CD>+<M>)}"

pron_atWhere = "<NN|LC>+<VV>?<P>?<CD>*<M>?<VE|AD><LOC>+"
pron_loc_grammar = "PDIS: {<PN>"+pron_atWhere+"(<PU>"+pron_atWhere+")*"+"}"

# wosub_grammar = "DWOS: {<VV|P><P>?<LOC|NR>+<VV>?(<LC>|<CD>+<M>|<LC><VV>?<CD>+<M>)}" # distance without subject

dir_dis = "(<CD>+<M>|<LC><VV>?<CD>+<M>|<LC>)"  # 距離&方位描述
rel_loc = "<LOC|NR>+(<PU><LOC|NR>)*"  # 相對地點
stdWhere = '<VV|P><P>?'+rel_loc+'<AD>?<VV>?'+dir_dis  # standard where <去/在/居...> <相對地點> <何方幾里>
dirWhere = "<LC>(<AD><VV>|<VV>|<AD>)<LOC|NR>(<CD>+<M>)?"
atWhere = f"(({stdWhere})|({dirWhere}))"
full_grammar = "DISF: {<P>?<LOC|NR>+<CNTRY>?<AD>?"+atWhere+"((<PU>"+atWhere+")*)}"

loc_parser = RegexpParser(loc_grammar)
pron_loc_parser = RegexpParser(pron_loc_grammar)
full_grammar_parser = RegexpParser(full_grammar)

sentences_t = list(zip(*list(json_t.values())))
# for every sentence (sentence == [[tok list],[pos list],[ner list],[sdp list]])
lst = []
lst2 = []
chunks = []
chunks_rev = []
for sentence in sentences_t:
    # unzip to [word_tuple, word_tuple, ...]; word_tuple = (tok, pos, ner, sdp)
    sentence = list(sentence)
    
    sdp = sentence.pop(3)
    ner = sentence.pop(2)
    ner = dict([(a, b) for a, b, c, d in ner])
    
    words = list(zip(*sentence))
    logging.debug(words)
    inserts = 0
    for N, thing in enumerate(words):
        n = N #+ inserts
        w, pos = thing
        if pos == 'NR' and ner.get(w) == "LOCATION" or w in LOCATIONS:
            words[n] = (w, 'LOC')
            # print(w, 'LOCATION')
        #elif pos == 'NR' and ner.get(w) != "PERSON":
            #words[n] = (w, 'LOC')
            # print(w, 'not LOCATION not PERSON')
        # elif pos == 'NR': print(w, 'PERSON')
        if pos == 'NN' and any([direction in w for direction in '東西南北']):
            words[n] = (w, 'LC')
        if w == "國":  # tag the character 國 as CNTRY
            words[n] = (w, 'CNTRY')
        '''if w == '其' and pos == "PN":
            print(''.join(sentence[0]))
            print(HanLP.coreference_resolution(''.join(sentence[0])))'''
        # 京西
        if pos in ('LOC', "NR") and any([w.endswith(direction) for direction in '東西南北']):
            words[n] = (w[:-1], 'LOC')
            words.insert(n+1, (w[-1], 'LC'))
            inserts += 1
        #篩掉 VV = 云 行 得 出 AD=猶
        if (w in '云行得出' and pos == 'VV') or (w=='猶' and pos=='AD'):
            words[n] = (w, pos+"XCP")

    lst.append(loc_parser.parse(words))
    lst2.append(pron_loc_parser.parse(words))
    lst2.append(full_grammar_parser.parse(words))

    

# extract DIS chunks
for sentence in lst2:
    for subtree in sentence:
        if isinstance(subtree, Tree) and (subtree.label() == 'DISF' or subtree.label() == 'PDIS'):   # DIS PDIS 
            if any(['使' in i[0] for i in tuple(subtree)]):  # why????
                continue
            else:
                #if subtree.label() == 'DIS':
                chunks.append(tuple(subtree))
                #elif subtree.label() == 'PDIS':
                chunks_rev.append(subtree.label())
                # print(subtree)  # commented 0410
                print(''.join(list(zip(*subtree))[0]))
                # print('')  # commented 0410

# perhaps we can use regex to filter?
"""
# Write to table (csv file)
with open('results.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['國名','治所','相對地點','方位','里程'])
    for lines, lbl in zip(chunks, chunks_rev):
        # print(line, lbl)
        w = ("，", "PU")
        spl = [list(y) for x, y in groupby(lines, lambda z: z == w) if not x]
        for line in spl:
            data = ['' for i in range(5)]
            
            # split "line" in python with VV and CD as the delimiter to know the Subject + Object + UNIT
            # if [vv not in line] use p to split
            if not any([i[1] == 'VV' for i in line[:4]]): 
                if any([i[1] == 'P' for i in line]):
                    line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("P", "CD")) if not k]  # split list by i[1] == ("P", "CD")
                else:
                    line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("LOC", "NR"))]  # split list by i[1] == ("LOC", "NR")
            else:
                line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("VV", "CD")) if not k]
            line_group= line_group[::-1]
            if len(line_group) > 1:
                locs_s = [name for name, pos in line_group[1] if pos not in ('AD', 'LC', 'VE')]# in ('LOC','NR', 'PN')] # subject
            else:
                locs_s = []
            locs_o = [name for name, pos in line_group[0] if pos not in ("LC", "VV", "VE", "M", "AD")] #in ('LOC','NR', 'PN')] # object
            if lbl == "PDIS":
                if len(locs_s): data[2] = ''.join(locs_s)
                data[0] = ''.join(locs_o)
            else:
                if len(locs_s): data[0] = ''.join(locs_s)
                data[2] = ''.join(locs_o)
            
            # capital
            data[1] = ''
            
            data[3] = ''.join([name for name, pos in line if pos == 'LC' or pos == 'NN'])
            data[4] = ''.join([name for name, pos in line if pos == 'CD' or pos == 'M'])
            if data[4] != '' and '數' not in data[4]:
                data[4] = str(chineseNumeralsToInteger(data[4])) + ''.join([ch for ch in data[4] if ch not in map_nums])
            writer.writerow(data)
"""
filecsv.close()
filetxt.close()