# -*- coding: utf-8 -*-
"""
Created on Sun Feb 26 22:42:58 2023

@author: alexh
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
"""
string = '''大宛      	專有名詞 
國       	其他名詞 
去       	其他動詞 
長安      	專有名詞 
萬二千五百五十 	概數詞 
里       	量詞  
，       	標點符號 
東       	其他名詞 
至       	其他動詞 
都護治     	專有名詞 
，       	標點符號 
西南      	其他名詞 
至       	其他動詞 
大月氏     	專有名詞 
，       	標點符號 
南       	其他名詞 
亦       	副詞
至       	其他動詞 
大月氏     	專有名詞 
，       	標點符號 
北       	其他名詞 
至       	其他動詞 
康居      	專有名詞 
。       	標點符號 '''
lst = []
for line in string.split('\n'):
    lst.append(line.split())
    
lst = list(map(list, zip(*lst)))
for a in lst:
    print(*a, sep='\t')"""
    
    
answer = '''大宛	國	去	長安	萬二千五百五十	里	，	東	至	都護	治	，	西南	至	大月氏	，	南	亦	至	大月氏	，	北	至	康居	。'''.split('\t')
jiayan = '''大宛	國	去	長	安	萬	二千	五百	五十	里	，	東	至	都	護	治	，	西南	至	大月氏	，	南	亦	至	大月氏	，	北	至	康居	。'''.split('\t')
jieba = '''大宛	國去	長安	萬	二千五百	五十里	，	東至	都	護治	，	西南	至	大月氏	，	南亦	至	大月氏	，	北至	康居	。'''.split('\t')
stanza = '''大	宛	國	去	長	安萬二千五百五十	里	，	東	至	都護	治	，	西南	至	大	月	氏	，南	亦	至	大	月	氏	，	北	至	康居	。'''.split('\t')
hanlp = '''大宛	國	去	長安	萬二千五百五十	里	，	東	至	都護治	，	西南	至	大月氏	，	南	亦	至	大月氏	，	北	至	康居	。'''.split('\t')
jiayan_anb = [x for x in answer if x in jiayan]
jieba_anb= [x for x in answer if x in jieba]
stanza_anb= [x for x in answer if x in stanza]
hanlp_anb= [x for x in answer if x in hanlp]

print("jiayan")
print("precision", len(jiayan_anb), len(jiayan))
print("recall", len(jiayan_anb), len(answer))
print()

print("jieba")
print("precision", len(jieba_anb), len(jieba))
print("recall", len(jieba_anb), len(answer))
print()


print("stanza")
print("precision", len(stanza_anb), len(stanza))
print("recall", len(stanza_anb), len(answer))
print()


print("hanlp")
print("precision", len(hanlp_anb), len(hanlp))
print("recall", len(hanlp_anb), len(answer))
print()




