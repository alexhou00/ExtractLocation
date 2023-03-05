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


class Word(NamedTuple):
    tok: str  # Tokenization
    pos: str  # Part of Speech
    sdp: list  # Semantic Dependency Parsing, 語義依存分析
    ner: list = ['',0,0] # Named Entity Recognition, 命名實體識別
 
for name, logger in logging.root.manager.loggerDict.items():
    logger.disabled=True
logging.basicConfig(level=logging.INFO)

books = ['史記v123', '漢書v96', '後漢書v88']
# Read Original text (text preprocessing, xml -> str)
texts = []
with open(f'文本/{books[0]}.xml', 'r', encoding='utf-8') as f:
    for line in f:
        # remove ascii chars, which means to delete <tags>
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
        if line.endswith('</s>\n'): texts.append('\n')


text = ''.join(texts)

# Fill in auth (auth=None -> anonymous), set language='zh' to use Chinese models
HanLP = HanLPClient('https://www.hanlp.com/api', auth=os.environ['API_KEY'], language='zh')

# Use tasks=[...] to run selected tasks only
# type(t) = Document()  # (Document object of hanlp_common.document)
t = HanLP(text, tasks=['pos', 'ner', 'sdp'])

LOCATIONS = ['烏孫']

json_t = json.loads(str(t))
logging.debug(str(t))

filecsv = open('test_hanlp_findloc.csv', 'a', encoding='utf-8', newline='')
filetxt = open('test_hanlp_findloc.txt', 'a', encoding='utf-8')
writer = csv.writer(filecsv)

loc_grammar = "DIS: {<P>?<LOC|NR>+<CNTRY>?<AD>?<VV|P><P>?<LOC|NR>+<AD>?<VV>?(<LC><VV>?<CD>+<M>|<LC>|<CD>+<M>)}"
pron_loc_grammar = "PDIS: {<PN><NN|LC>+<VV><P>?<CD>*<M>?<VE><LOC>+}"
wosub_grammar = "DWOS: {<VV|P><P>?<LOC|NR>+<VV>?(<LC>|<CD>+<M>|<LC><VV>?<CD>+<M>)}" # distance without subject
loc_parser = RegexpParser(loc_grammar)
pron_loc_parser = RegexpParser(pron_loc_grammar)

sentences_t = list(zip(*list(json_t.values())))
# for every sentence (sentence == [[tok list],[pos list],[ner list],[sdp list]])
lst = []
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
        if pos == 'NR' and ner.get(w) == "LOCATION":
            words[n] = (w, 'LOC')
            # print(w, 'LOCATION')
        #elif pos == 'NR' and ner.get(w) != "PERSON":
            #words[n] = (w, 'LOC')
            # print(w, 'not LOCATION not PERSON')
        # elif pos == 'NR': print(w, 'PERSON')
        if pos == 'NN' and any([direction in w for direction in '東西南北']):
            words[n] = (w, 'LC')
        if w == "國":
            words[n] = (w, 'CNTRY')
        '''if w == '其' and pos == "PN":
            print(''.join(sentence[0]))
            print(HanLP.coreference_resolution(''.join(sentence[0])))'''
        # 京西
        if pos in ('LOC', "NR") and any([w.endswith(direction) for direction in '東西南北']):
            words[n] = (w[:-1], 'LOC')
            words.insert(n+1, (w[-1], 'LC'))
            inserts += 1

    lst.append(loc_parser.parse(words))
    lst.append(pron_loc_parser.parse(words))

    

# extract DIS chunks
for sentence in lst:
    for subtree in sentence:
        if isinstance(subtree, Tree) and (subtree.label() == 'DIS' or subtree.label() == 'PDIS'):  
            if any(['使' in i[0] for i in tuple(subtree)]):
                continue
            else:
                #if subtree.label() == 'DIS':
                chunks.append(tuple(subtree))
                #elif subtree.label() == 'PDIS':
                chunks_rev.append(subtree.label())
                print(subtree)
                print(''.join(list(zip(*subtree))[0]))
                print('')

with open('results.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['國名','治所','相對地點','方位','里程'])
    for line, lbl in zip(chunks, chunks_rev):
        data = ['' for i in range(5)]
        
        # split "line" in python with VV and CD as the delimiter to know the Subject + Object + UNIT
        # if [vv not in line] use p to split
        if not any([i[1] == 'VV' for i in line[:4]]): 
            if any([i[1] == 'P' for i in line]):
                line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("P", "CD")) if not k]
            else:
                line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("LOC", "NR"))]
        else:
            line_group = [list(group) for k, group in groupby(line, lambda x: x[1] in ("VV", "CD")) if not k]
            
        locs_s = [name for name, pos in line_group[0] if pos not in ('AD', 'LC', 'VE')]# in ('LOC','NR', 'PN')] # subject
        locs_o = [name for name, pos in line_group[1] if pos not in ("LC", "VV", "VE", "M", "AD")] #in ('LOC','NR', 'PN')] # object
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


filecsv.close()
filetxt.close()