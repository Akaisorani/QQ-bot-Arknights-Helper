import requests
import urllib
from html import unescape
from lxml import html
import re
import os, sys

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

class Jd_tuchuang(object):
    def __init__(self):
        self.url="https://search.jd.com/image?op=upload"


    def upload(self, imgfile):
        # session=requests.Session()
        # r=session.get("https://www.jd.com")

        files = { 'file':open(imgfile,'rb') }
        headers={
            'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,ja;q=0.7',
            # 'cache-control': 'max-age=0',
            # 'cookie': 'shshshfpa=cf6abfac-73f6-6f03-cee9-822cfe92fbad-1535427871; shshshfpb=0513238f4019531447b4f364954244bb295b73d561c451ccb5b84c51e3; pinId=q2Z5p-4bcPy8iKCOQ8MMNQ; qrsc=3; TrackID=1Xe04zYOvfSN1GU1FJorf5TAbpw9mKbq62Qo6j7wgDq1PW8ojf3T3Z1lAOyUTCXgcbmH2KgAnN5_DOpfqAir2K7yAjo469ju5QIDKgUp6dOc; __jdu=1535427869971124336637; xtest=6037.cf6b6759; __jdv=76161171|direct|-|none|-|1564229351913; areaId=1; ipLoc-djd=1-2800-0-0; PCSYCityID=CN_110000_110100_110108; __jda=76161171.1535427869971124336637.1535427870.1564229352.1564233416.11; __jdb=76161171.1.1535427869971124336637|11.1564233416; __jdc=76161171; shshshfp=72260dd734b0f31fb2843b2ae2e3c6ab; shshshsID=fc051646e1759f064c941c28ee6027f1_1_1564233418920',
            'origin': 'https://search.jd.com',
            # 'referer': 'https://search.jd.com/image?path=jfs%2Ft1%2F65884%2F33%2F5649%2F917269%2F5d3c4112E96a2fcb6%2F4086b85b116c9efb.png&op=search',
            # 'upgrade-insecure-requests': '1'
            # '?op=upload'
        }
        # params={'op':'upload'}
        # headers={}
        # req=requests.Request('POST',self.url,files=files,headers=headers,data=params).prepare()
        # print(req.headers)
        # session=requests.Session()
        # r=session.send(req)
        r=requests.post(self.url,files=files,headers=headers)
        if r.status_code!=200:
            print("MY DEBUG uploadimg failed ",r.text)
            return None

        res = re.findall('callback[(]["](.*)["][)]', r.text)
        if not res or 'ERROR' in res[0]:
            print("MY DEBUG uploadimg failed ",res)
            print(r.text)
            return None            

        imgurl='http://img11.360buyimg.com/uba/'+res[0]
        


        return imgurl
        


if __name__=="__main__":
    jdtuc=Jd_tuchuang()
    # resurl=jdtuc.upload(o_path+"image.jpg")
    resurl=jdtuc.upload(o_path+"75893870_7.png")


    print(resurl)

