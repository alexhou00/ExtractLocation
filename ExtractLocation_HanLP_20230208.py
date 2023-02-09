# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 11:33:49 2023

@author: alexhou00

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

from urllib.error import HTTPError

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
    
# Read Original text (text preprocessing, xml -> str)
texts = []
with open('文本/史記v123.xml', 'r', encoding='utf-8') as f:
    for line in f:
        # remove ascii chars, which means to delete <tags>
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
text = ''.join(texts)

# Fill in auth (auth=None -> anonymous), set language='zh' to use Chinese models
HanLP = HanLPClient('https://www.hanlp.com/api', auth=os.environ['API_KEY'], language='zh')

# Use tasks=[...] to run selected tasks only
# type(t) = Document()  # (Document object of hanlp_common.document)
try:
    t = HanLP(text, tasks=['pos', 'ner', 'sdp'])
except HTTPError:
    logging.critical("Exceeded rate limiting of 2 per minute for anonymous user. 尊敬的匿名用户，你的调用次数超过了每分钟2次。 Please consider applying for a free auth at https://bbs.hankcs.com/t/topic/3178  由于服务器算力有限，匿名用户每分钟限2次调用。如果你需要更多调用次数，建议申请免费公益API秘钥auth https://bbs.hanlp.com/t/hanlp2-1-restful-api/53 ")
    quit()


json_t = json.loads(str(t))
logging.debug(str(t))

filecsv = open('test_hanlp_findloc.csv', 'a', encoding='utf-8', newline='')
filetxt = open('test_hanlp_findloc.txt', 'a', encoding='utf-8')
writer = csv.writer(filecsv)

loc_grammar = "DIS: {<LOC>+<VV><P>?<LOC>+(<LC|NN>|<CD>+<M>)}"
pron_loc_grammar = "PDIS: {<PN><NN|LC>+<VV><P>?<CD>*<M>?<VE><LOC>+}"
loc_parser = RegexpParser(loc_grammar)
pron_loc_parser = RegexpParser(pron_loc_grammar)

sentences_t = list(zip(*list(json_t.values())))
# for every sentence (sentence == [[tok list],[pos list],[ner list],[sdp list]])
lst = []
chunks = []
for sentence in sentences_t:
    # unzip to [word_tuple, word_tuple, ...]; word_tuple = (tok, pos, ner, sdp)
    sentence = list(sentence)
    sdp = sentence.pop(3)
    ner = sentence.pop(2)
    ner = dict([(a, b) for a, b, c, d in ner])
    words = list(zip(*sentence))
    logging.debug(words)
    for n, thing in enumerate(words):
        char, pos = thing
        if pos == 'NR' and ner.get(char) == "LOCATION":
            words[n] = (char, 'LOC')

    lst.append(loc_parser.parse(words))
    lst.append(pron_loc_parser.parse(words))

    

# extract NP chunks
for sentence in lst:
    for subtree in sentence:
        if isinstance(subtree, Tree) and (subtree.label() == 'DIS' or subtree.label() == 'PDIS'):  
            chunks.append(tuple(subtree))
            print(subtree)

with open('results.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['國名','治所','相對地點','方位','里程'])
    for line in chunks:
        data = ['' for i in range(5)]
        locs = [name for name, pos in line if pos == 'LOC' or pos == 'PN']
        data[0] = locs[0]
        data[1] = ''
        data[2] = locs[1]
        data[3] = ''.join([name for name, pos in line if pos == 'LC' or pos == 'NN'])
        data[4] = ''.join([name for name, pos in line if pos == 'CD' or pos == 'M'])
        writer.writerow(data)
'''
>>> pos_tag(word_tokenize("John's big idea isn't all that bad.")) 
[('John', 'NNP'), ("'s", 'POS'), ('big', 'JJ'), ('idea', 'NN'), ('is', 'VBZ'),
("n't", 'RB'), ('all', 'PDT'), ('that', 'DT'), ('bad', 'JJ'), ('.', '.')]
'''

filecsv.close()
filetxt.close()