from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from xpinyin import Pinyin

class Fuzzname(object):
    def __init__(self):
        self.fuzzymap=dict()
        self.pinyin=Pinyin()

    def fit(self, namelis):
        self.fuzzymap=dict()
        for name in namelis:
            self.fuzzymap[name+" "+self.pinyin.get_pinyin(name,'')]=name

    def predict(self, name):
        namepin=name+" "+self.pinyin.get_pinyin(name,'')
        res=process.extractOne(namepin,self.fuzzymap.keys())
        res=self.fuzzymap[res[0]]
        return res