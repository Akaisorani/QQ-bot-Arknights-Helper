import os, sys

o_path = os.getcwd()
o_path=o_path+"/../../"
sys.path.append(o_path)

from aip import AipOcr
from apikeys import *
from PIL import Image
from io import BytesIO
import requests


class Ocr_tool(object):
    def __init__(self):
        self.client=AipOcr(APP_ID, API_KEY, SECRET_KEY)
        self.p_thres=0.5

    def get_file_content(self,filepath):
        with open(filepath, 'rb') as fp:
            return fp.read()
            
    def read_image(self,filepath):
        return Image.open(filepath)
        
    def crop_image(self,im):
        width, height=im.size
        im=im.crop((int(width*627/2160), int(height*531/1080), int(width*1421/2160), int(height*737/1080)))
        return im
    
    def show_im(self,im):
        im.show()
        
    def image2byte(self, im):
        out_buffer=BytesIO()
        im.save(out_buffer, format='JPEG')
        byte_data = out_buffer.getvalue()
        return byte_data
        
    def ocr(self, im):
        byte_data=self.image2byte(im)
        options = {}
        options["language_type"] = "CHN_ENG"
        options["probability"] = "true"
        res=self.client.basicGeneral(byte_data, options)
        
        word_lis=[]
        for word_entry in res["words_result"]:
            if word_entry["probability"]["average"]<self.p_thres:continue
            word_lis.append(word_entry["words"])
            
        return word_lis
        
    def get_im_from_url(self, imgurl):
        r=requests.get(imgurl,timeout=30)
        buffer=r.content
        im=Image.open(BytesIO(buffer))
        return im
        
        
    def get_tags_from_url(self, imgurl):
        im=self.get_im_from_url(imgurl)
        im=self.crop_image(im)
        tag_lis=self.ocr(im)
        return tag_lis
        
        
        
if __name__=="__main__":
    ocr_t=Ocr_tool()
    url="https://c2cpicdw.qpic.cn/offpic_new/1224067801//39b40a48-b543-4082-986d-f29ee82645d3/0?vuin=2473990407&amp;amp;term=2"
    # im=ocr_t.read_image("tags.jpg")
    # im=ocr_t.crop_image(im)
    # word_lis=ocr_t.ocr(im)
    res=ocr_t.get_tags_from_url(url)
    print(res)
        
            
    
        

