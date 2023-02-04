# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 22:54:39 2023


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

from urllib.error import HTTPError

import logging

import json
import csv


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
HanLP = HanLPClient('https://www.hanlp.com/api', auth=None, language='zh')

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

sentences_t = list(zip(*list(json_t.values())))
# for every sentence (sentence == [[tok list],[pos list],[ner list],[sdp list]])
for sentence in sentences_t:
    # unzip to [word_tuple, word_tuple, ...]; word_tuple = (tok, pos, ner, sdp)
    sentence = list(sentence)
    ner = sentence.pop(2)
    ner = dict([(a, [b,c,d]) for a, b, c, d in ner])
    words = list(zip(*sentence))
    
    words = [list(word) for word in words]
    for word in words:
        if word[0] in ner:
            word.append(ner[word[0]])
        else:
            word.append(['',0,0])
    
    # find grammar: "NR+LOCATION", "VV", "NR+LOCATION", "CD", "M"
    # words = [word, word, word, ...]
    # word = ["", "", [], []] # tok, pos, sdp, ner
    #with open('test_hanlp_findloc.csv', 'a', encoding='utf-8') as f:
    for word in words:
        if word[3][0] == 'LOCATION':
            for line in list(zip(*[(word[0], word[1], str(word[2])) for word in words])):
                writer.writerow(line)
                filetxt.write(''.join(line)+'/n')
            break
    grammarTable = [
        ['NR', 'VV', 'NR', 'CD', 'M'], # 康居國 在 京西 一萬六百 里 
        ['NR', 'VV', 'NR', 'CD', 'CD', 'M'], #
        ['NR', 'VV', 'P', 'NR', 'CD', 'M'], # 拘彌國 去 于 窴 三百 里
        ['NR', 'VV', 'P', 'NR', 'CD', 'CD', 'M'],
        ['NR', 'VV', 'NR', 'LC'], # LC -> , 'NN' # 蒲昌海 在 蒲類海 東; 祁連山 在 甘州 西南
        
        ['PN', 'NN', 'VV', 'CD', 'M', 'VE', 'NR'], # 其 西北 可 二千 里 有 奄蔡
        ['PN', 'NN', 'VV', 'CD', 'CD', 'M', 'VE', 'NR'],
        ]
    # 2nd NR -> NR PU NR
    # to do: 都 capital
    for grammarRule in grammarTable:
        for i in range(len(words)-len(grammarRule)+1):
            # word = words[i]
            #if i <= len(words)-5: # of course, if is range(len(words)-4)
                #for j, tag in enumerate(grammarRule):
            if all ([words[i+j][1] == tag for j, tag in enumerate(grammarRule)]):
                for k in range(i, i+len(grammarRule)):
                    print(words[k][0], end='')
                print()
            
            

filecsv.close()
filetxt.close()