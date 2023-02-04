# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 14:34:43 2023

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
"""
# text preprocess (xml -> pure text) => tokenization
# => tag PoS => parse grammar (place is at where)


from jiayan import CRFPOSTagger
from jiayan import load_lm #, WordNgramTokenizer
from jiayan import CharHMMTokenizer
import csv
texts = []
with open('文本/史記v123.xml', 'r', encoding='utf-8') as f:
    for line in f:
        texts.append(''.join([i if ord(i) > 128 else '' for i in line]))
text = ''.join(texts)
# tokenizer = WordNgramTokenizer()

lm = load_lm('jiayan_models/jiayan_models/jiayan.klm')
tokenizer = CharHMMTokenizer(lm)



words = list(tokenizer.tokenize(text))

postagger = CRFPOSTagger()
postagger.load('jiayan_models/jiayan_models/pos_model')
pos = postagger.postag(words)
wordswPoS = list(zip(words, pos))

pos_meaning = dict()
with open('pos_meaning.csv', 'r', encoding='utf-8-sig') as f:
    csvreader = csv.reader(f)
    for row in csvreader:
        pos_meaning[row[0]] = row[1]

formatted = [word.ljust(5,'　')+' '+pos_meaning[pos].rjust(20) for word, pos in wordswPoS]


for i,j in enumerate(wordswPoS):
    if j[1] == 'ns':
        print(j[0])
        
with open('results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(formatted))