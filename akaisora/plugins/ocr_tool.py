import os, sys

o_path = os.getcwd()
# o_path=o_path+"/../../"
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
        im.save(out_buffer, format='PNG')
        byte_data = out_buffer.getvalue()
        return byte_data
        
    def ocr(self, image=None, url=None):
        options = {}
        options["language_type"] = "CHN_ENG"
        options["probability"] = "true"
        if image is not None:
            byte_data=self.image2byte(image)
            res=self.client.basicGeneral(byte_data, options)
        elif url is not None:
            res=self.client.basicGeneralUrl(url, options)
        else:
            return []
        print(res)
        word_lis=[]
        if "words_result" in res:
            for word_entry in res["words_result"]:
                if word_entry["probability"]["average"]<self.p_thres:continue
                word_lis.append(word_entry["words"])
            
        return word_lis
        
    def get_im_from_url(self, imgurl):
        r=requests.get(imgurl,timeout=30)
        buffer=r.content
        im=Image.open(BytesIO(buffer))
        return im
        
        
    def get_tags_from_url(self, imgurl, crop=False):
        if crop:
            im=self.get_im_from_url(imgurl)
            if im.mode=='P':
                print("MYDEBUG mode:P")
                return []
            im=self.crop_image(im)
            tag_lis=self.ocr(image=im)
        else:
            tag_lis=self.ocr(url=imgurl)
        
        return tag_lis
        
        
        
if __name__=="__main__":
    ocr_t=Ocr_tool()
    url="https://c2cpicdw.qpic.cn/offpic_new/1224067801//39b40a48-b543-4082-986d-f29ee82645d3/0?vuin=2473990407&amp;amp;term=2"
    url="https://gchat.qpic.cn/gchatpic_new/928486287/698793878-2394576410-EFE27EE550AA2B1E68923AD3A227A9B1/0?vuin=2473990407&amp;amp;term=2"
    url="https://c2cpicdw.qpic.cn/offpic_new/391809494//857ddb74-7a0d-40ae-98db-068f8c733c86/0?vuin=2473990407&amp;amp;term=2"
    url="https://s2.ax1x.com/2019/07/08/ZspCnJ.jpg"
    # im=ocr_t.read_image("tags.jpg")
    # im=ocr_t.crop_image(im)
    # word_lis=ocr_t.ocr(im)
    res=ocr_t.get_tags_from_url(url)
    print(res)
        
            
    
        

