import os, sys
o_path = os.getcwd()
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

import csv
import requests
import urllib
from html import unescape
from lxml import html
from fuzzname import Fuzzname

class Material(object):
    def __init__(self):
        self.material_data=dict()
        self.columns_name=[]
        self.name_lis=[]
        self.fuzzname=Fuzzname()

        self.load_data(o_path+"res.csv")
    
    def load_data(self, filename):
        self.material_data=dict()
        self.name_lis=[]
        with open(filename,encoding='UTF-8') as fp:
            csv_reader=csv.reader(fp)
            self.columns_name=next(csv_reader)[:5]
            for line in csv_reader:
                name=line[0]
                self.material_data[name]=dict(list(zip(self.columns_name[0:5],line[0:5])))
                self.name_lis.append(name)

        self.fuzzname.fit(self.material_data.keys())
    
    def format(self, name):
        # lines=[]
        # lines.append(["\t"]+self.columns_name[1:4])
        # lines.append([name]+[self.material_data[name][colname] for colname in self.columns_name[1:4]])
        # lines.append([self.columns_name[4]+":"+self.material_data[name][self.columns_name[4]]])
        # res="\n".join(["\t".join(line) for line in lines])
        reslis=[]
        reslis.append(name+"  "+self.material_data[name]["材料等级"]+"色")
        for colname in self.columns_name[2:5]:
            if self.material_data[name][colname]:
                reslis.append("{0}: {1}".format(colname, self.material_data[name][colname]))
        res="\n".join(reslis)
        return res

    def recom(self, name):
        if not name: return None
        if name not in self.material_data:
            name=self.fuzzname.predict(name)
        res=self.format(name)
        return res

    def export_table_md(self):
        self.fetch_wiki()
        item_lis=["img_div"]+self.columns_name[:5]
        with open(o_path+"materials.md","w",encoding='UTF-8') as fp:
            fp.write("# 刷材料推荐地点\n\n")
            fp.write("<table>\n")
            fp.write("<tr>\n")
            for colname in [""]+self.columns_name[:5]:
                fp.write("<td>")
                fp.write(colname)
                fp.write("</td>\n")
            fp.write("</tr>\n")

            for name in self.name_lis:
                fp.write("<tr>\n")
                
                for item_name in item_lis:
                    fp.write("<td>")
                    fp.write(self.material_data[name][item_name])
                    fp.write("</td>\n")

                fp.write("</tr>\n")
            fp.write("</table>\n")

    def fetch_wiki(self):
        url_prefix="http://wiki.joyme.com"
        r=requests.get(url_prefix+"/arknights/材料")
        tree=html.fromstring(r.text)
    
        mati_lis=tree.xpath("//span[@class='itemhover']/div[1]")
        for mati in mati_lis:
            name=mati.xpath("./a/@title")[0]
            if name and name in self.material_data:
                sub_link=mati.xpath("./a/@href")[0]
                self.material_data[name]["link"]=url_prefix+sub_link
                self.material_data[name]["img"]=mati.xpath("./a/img/@src")[0]
                self.material_data[name]["img_div"]=unescape(html.tostring(mati).decode('utf-8')).replace(sub_link,self.material_data[name]["link"])

        
if __name__=="__main__":
    material_recom=Material()
    res=material_recom.recom("聚酸酯块")
    print(res)

    material_recom.export_table_md()
    print(material_recom.material_data["聚酸酯块"])