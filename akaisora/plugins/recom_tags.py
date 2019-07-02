from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
import requests
import urllib
from html import unescape
from lxml import html
import os, sys

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from xpinyin import Pinyin

o_path = os.getcwd()
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

from ocr_tool import Ocr_tool

path_prefix="./akaisora/plugins/"
# path_prefix=""

# some comments below is from the demo code of nonebot

# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('tagrc', aliases=(), only_to_me=False)
async def tagrc(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # tags = session.get('tags', prompt='输入tag列表，空格隔开')
    tags=session.state['tags'] if 'tags' in session.state else None
    images=session.state['images'] if 'images' in session.state else None
    if not tags and not images:return
    # 获取城市的天气预报
    tagrc_report = await get_recomm_tags(tags=tags,images=images)
    if tagrc_report is None: return 
    # 向用户发送天气预报
    await session.send(tagrc_report)
    
@on_command('hello', aliases=(), only_to_me=True)
async def hello(session: CommandSession):

    info_msg="""明日方舟 公开招募助手机器人
用法:
1.输入词条列表，空格隔开
    如: 近卫 男
2.发送招募词条截图
    
3.tell 干员名称
    如: tell 艾雅法拉
Github链接: https://github.com/Akaisorani/QQ-bot-Arknights-Helper"""

    await session.send(info_msg)
    
@on_command('update_data', aliases=(), only_to_me=True)
async def update_data(session: CommandSession):

    tags_recom.char_data.fetch_data()
    tags_recom.char_data.extract_all_char(text_file=path_prefix+"chardata.html")
    
    
    info_msg="update done"

    await session.send(info_msg)
    
@on_command('tell', aliases=(), only_to_me=False)
async def tell(session: CommandSession):
    name=session.state['name'] if 'name' in session.state else None
    if not name :return
    # 获取城市的天气预报
    tell_report = await get_peo_info(name=name)
    if tell_report is None: return 
    # 向用户发送天气预报
    await session.send(tell_report)

# weather.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@tagrc.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    images_arg=session.current_arg_images
    
    print("stripped_arg", stripped_arg)
    print("images_arg", images_arg)
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['tags'] = stripped_arg
        elif images_arg:
            session.state['images'] = images_arg
        return

    # if not stripped_arg:
        # # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        # session.pause('输入错误，请重新输入')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    # session.state[session.current_key] = stripped_arg

# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(only_to_me=False, keywords=None)
async def _(session: NLPSession):

    # stripped_msg = session.msg_text.strip()
    msg=session.msg

    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'tagrc', current_arg=msg or '')
    
@tell.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    
    print("tell stripped_arg", stripped_arg)
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['name'] = stripped_arg
        return


async def get_recomm_tags(tags: str, images: list) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    tags_list=tags.split() if tags else []
    report=tags_recom.recom(tags_list, images)
    
    return report
    
async def get_peo_info(name: str) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    report=tags_recom.char_data.get_peo_info(name)
    
    return report


class Character(object):
    def __init__(self):
        self.char_data=dict()
        self.head_data=[]
        self.head_key_map={
            "职业":"job",
            "星级":"rank",
            "性别":"sex",
            "阵营":"affiliation",
            "标签":"tags",
            "获取途径":"obtain_method"
        }
        self.fuzzymap=dict()
        self.pinyin=Pinyin()
        
    def extract_all_char(self, text_string=None, text_file=None, head_file=None):
        if text_file is None:text_file=path_prefix+"chardata.html"  
        if head_file is None:head_file=path_prefix+"data_head.html" 
        if not os.path.exists(text_file) or not os.path.exists(head_file):
            self.fetch_data()
        if text_string is None:
            with open(text_file,encoding='UTF-8') as fp:
                text_string=fp.read()
        with open(head_file,encoding='UTF-8') as fp:
            head_string=fp.read()
        self.head_data=head_string.split(',')

        tree=html.fromstring(text_string)
        char_res_lis=tree.xpath("//tr")
        
        self.char_data=dict()
        for char_tr in char_res_lis:
            name=char_tr.xpath("./td[2]/a[1]/text()")[0]
            self.char_data[name]=dict()
            self.char_data[name]["job"]=char_tr.xpath("./@data-param1")[0]
            self.char_data[name]["rank"]=char_tr.xpath("./@data-param2")[0].split(",")[0]
            self.char_data[name]["sex"]=char_tr.xpath("./@data-param3")[0]
            self.char_data[name]["affiliation"]=char_tr.xpath("./@data-param4")[0]
            tag_string=char_tr.xpath("./@data-param5")[0]+", " \
                        +self.char_data[name]["sex"]+", " \
                        +self.char_data[name]["job"]+", " \
                        +("资深干员" if self.char_data[name]["rank"]=="5" else "")+", " \
                        +("高级资深干员" if self.char_data[name]["rank"]=="6" else "")+", "
            taglist=[x.strip() for x in tag_string.split(",")]
            taglist=[x for x in taglist if x!=""]
            self.char_data[name]["tags"]=taglist
            self.char_data[name]["obtain_method"]=list(map(lambda x: x.strip(), char_tr.xpath("./@data-param6")[0].split(",")))
            
            #deal head and data
            td_lis=char_tr.xpath(".//td")
            text_lis=["".join([xx.strip() for xx in x.xpath(".//text()")]) for x in td_lis]
            all_lis=[x.strip() for x in text_lis]
            self.char_data[name]["all"]=all_lis
            
        # fuzzy name+pinyin -> name
        self.fuzzymap=dict()
        for name in self.char_data.keys():
            self.fuzzymap[name+" "+self.pinyin.get_pinyin(name,'')]=name
            
    def filter(self, tags):
        tags=tags[:]
        ranks=self.gen_ranks(tags)
        for name, dic in self.char_data.items():
            if set(tags).issubset(set(dic["tags"])) and "公开招募" in dic["obtain_method"] and dic["rank"] in ranks:
                yield name
     
    def gen_ranks(self, tags):
        ranks=["1","2","3","4","5","6"]
        for i in range(1,7):
            if ">={0}".format(i) in tags:
                ranks=[x for x in ranks if x>=str(i)]
                tags.remove(">={0}".format(i))
            if "<={0}".format(i) in tags:
                ranks=[x for x in ranks if x<=str(i)]
                tags.remove("<={0}".format(i))
        if "高级资深干员" not in tags:
            ranks.remove("6")
        if "资深干员" in tags:
            ranks=["5"]
        if "高级资深干员" in tags:
            ranks=["6"]
        return ranks
        
    def get_peo_info(self, name=None):
        if not name: return None
        if name not in self.char_data:
            namepin=name+" "+self.pinyin.get_pinyin(name,'')
            res=process.extractOne(namepin,self.fuzzymap.keys())
            res=self.fuzzymap[res[0]]
            return "你可能想查 {0}".format(res)
        res=[]
        for tp, cont in zip(self.head_data,self.char_data[name]['all']):
            if tp:
                if tp=="干员代号":tp="姓名"
                res.append("{0}: {1}".format(tp,cont))
        url_prefix="http://wiki.joyme.com/arknights/"
        url=url_prefix+urllib.parse.quote(name)
        res.append(url)
        
        return "\n".join(res)
        
    def fetch_data(self):
        r=requests.get("http://wiki.joyme.com/arknights/干员数据表")
        tree=html.fromstring(r.text)
        
        # people data
        people_list=tree.xpath("//tr[@data-param1]")
        res="".join([unescape(html.tostring(peo).decode('utf-8')) for peo in people_list])
        
        with open(path_prefix+"chardata.html","w",encoding='utf-8') as fp:
            fp.write(res)
        
        # table head data
        tb_head=tree.xpath("//table[@id='CardSelectTr']//th/text()")
        tb_head=[x.strip() for x in tb_head]
        with open(path_prefix+"data_head.html","w",encoding='utf-8') as fp:
            fp.write(",".join(tb_head))
                
class Tags_recom(object):
    def __init__(self):
        self.char_data=Character()
        self.char_data.extract_all_char(text_file=path_prefix+"chardata.html")
        self.all_tags={
        '狙击', '术师', '特种', '重装', '辅助', '先锋', '医疗', '近卫',
        '减速', '输出', '生存', '群攻', '爆发', '召唤', '快速复活','费用回复',
        '新手', '治疗', '防护', '位移', '削弱', '控场', '支援',
        '近战位', '远程位',
        '近战', '远程',
        '资深干员','高级资深干员', 
        '资深','高资', 
        '女', '男',
        '女性', '男性',
        '狙击干员', '术师干员', '特种干员', '重装干员', '辅助干员', '先锋干员', '医疗干员', '近卫干员',
        '女性干员', '男性干员'
        }  
        
        self.ocr_tool=Ocr_tool()
        
    def recom_tags(self, tags):
        tags=self.strip_tags(tags)
    
        itertag=self.iter_all_combine(tags)
        if itertag is None:return []
        cob_lis=list(itertag)
        cob_lis.remove([])
        cob_lis=[(tags_lis, list(self.char_data.filter(tags_lis))) for tags_lis in cob_lis]
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        
        # print("")
        # for x in cob_lis:
            # print(x)
        
        # remove same result
        for i in range(0,len(cob_lis)):
            for j in range(0,len(cob_lis)):
                if i==j:continue
                if set(cob_lis[i][1])==set(cob_lis[j][1]):
                    if set(cob_lis[i][0]).issubset(set(cob_lis[j][0])):
                        cob_lis[i]=(cob_lis[i][0],[])
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print("")
        # for x in cob_lis:
            # print(x)
   
        # special remove
        for i in range(len(cob_lis)):
            if self.is_special_rm(cob_lis[i]):
                cob_lis[i]=(cob_lis[i][0],[])
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print("")
        # for x in cob_lis:
            # print(x)   
        
        # sort
        cob_lis.sort(key=self.avg_rank, reverse=True)
        for tags_lis, lis in cob_lis:
            lis.sort(key=lambda x:self.char_data.char_data[x]["rank"], reverse=True)
        # print("")
        # for x in cob_lis:
            # print(x)
            
        # for x in cob_lis:
            # print(self.avg_rank(x))
            
        # # build reverse index
        # char_dic=dict()
        # for i in range(len(cob_lis)):
            # for name in cob_lis[i][1]:
                # if name not in char_dic:
                    # char_dic[name]=[i]
                # else:
                    # char_dic[name].append(i)
        # # print("")
        # # print(char_dic)
        
        # # remove duplicate
        # min_size_id=dict()
        # for name, lis in char_dic.items():
            # if len(lis)>1:
                # min_size_id[name]=lis[0]
                # for id in lis:
                    # if len(cob_lis[id][1])<len(cob_lis[min_size_id[name]][1]):
                        # min_size_id[name]=id
                        
        # for name, lis in char_dic.items():
            # if len(lis)>1:                        
                # for id in lis:
                    # if id!=min_size_id[name]:
                        # cob_lis[id][1].remove(name)
        # cob_lis=[x for x in cob_lis if x[1]!=[]]
        # # print("")
        # # for x in cob_lis:
            # # print(x)
        
        #merge less rank 3
        tag_cnt=0
        max_num_until_del=15
        for tags_lis, lis in cob_lis:
            cnt=0
            sp_lis=[]
            while len(lis)>0 and self.char_data.char_data[lis[-1]]["rank"]<="3":
                res=lis.pop()
                if res=="Castle-3":
                    sp_lis.append(res)
                else:
                    cnt+=1
            
            if len(sp_lis)>0:
                lis.extend(sp_lis)
            if cnt>0 and len(lis)>0:
                lis.append("...{0}".format(cnt))
                # delete all contain <=3
                if tag_cnt+len(lis)>max_num_until_del:
                    lis.clear()
                    max_num_until_del=-1
            tag_cnt+=len(lis)
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        
        return cob_lis
        # print("")
        # for x in cob_lis:
            # print(x)        
                
        
    
    def is_special_rm(self, cob_i):
        if set(cob_i[0])==set(["女"]):
            return True
        # if set(cob_i[0])==set(["男"]):
            # return True
        return False
        
    def avg_rank(self, cob_i):
        rank_map={1:0.5, 2:1, 3:10, 4:2, 5:0.5, 6:3}
        rank_list=list(map(lambda x:int(self.char_data.char_data[x]["rank"]),cob_i[1]))
        sum_score=0
        sum_cnt=0
        for i in range(1,7):
            sum_score+=rank_list.count(i)*rank_map[i]*i
            sum_cnt+=rank_list.count(i)*rank_map[i]
        if sum_cnt==0:return 0
        else: return sum_score/sum_cnt
    
    def strip_tags(self, tags):
        restags=[]
        for tag in tags:
            if tag in ["高级资深干员","高资"]:
                restags.append("高级资深干员")
            elif tag in ["资深干员","资深"]:
                restags.append("资深干员")
            elif tag in ["近战","远程"]:
                restags.append(tag+"位")
            elif tag in ["男性","女性"]:
                tag=tag.replace("性","")
                restags.append(tag)              
            elif "性干员" in tag:
                tag=tag.replace("性干员","")
                restags.append(tag)
            elif "干员" in tag:
                tag=tag.replace("干员","")
                restags.append(tag)
            else:
                restags.append(tag)
        return restags
        
    def iter_all_combine(self, tags):
        if len(tags)==0:
            yield []
            return
        tag=tags[0]
        new_tags=tags[:]
        new_tags.remove(tag)
        for x in self.iter_all_combine(new_tags):
            yield [tag]+x
        for x in self.iter_all_combine(new_tags):
            yield x
    
    def check_legal_tags(self, tags):
        if not tags: return False
        for tag in tags:
            if tag not in self.all_tags:
                return False
        return True
        
    def filter_legal_tags(self, tags):
        if not tags: return []
        res=[]
        for tag in tags:
            if tag in self.all_tags:
                res.append(tag)
        return res
    
    def recom(self, tags=None, images=None):
        if not tags:
            if images:
                tags=self.get_tags_from_image(images)
                if not tags:
                    print("MYDEBUG image checkfail {0}".format(images[0]))
                    return None
            else:
                return None
        
        if not self.check_legal_tags(tags):
            print("MYDEBUG no legal tags")
            return None
        cob_lis=self.recom_tags(tags)
        if not cob_lis:
            return "没有或者太多"
        line_lis=[]
        for tags_lis, lis in cob_lis:
            new_lis=[]
            for x in lis:
                if x in self.char_data.char_data:
                    new_lis.append(x+"★"+self.char_data.char_data[x]["rank"])
                else:
                    new_lis.append("★1~3"+x)
            lef='【'+'+'.join(tags_lis)+"】:\n"
            rig=', '.join(new_lis)
            line_lis.append(lef+rig)
        res="\n\n".join(line_lis)
        return res
    
    def get_tags_from_image(self, images):
        tags=self.ocr_tool.get_tags_from_url(images[0])
        tags=self.filter_legal_tags(tags)
        if len(tags)>=2:
            return tags
        else:
            return []
        
        

tags_recom=Tags_recom()

if __name__=="__main__":
    filename="chardata.html"
    char_data=Character()
    char_data.extract_all_char(text_file=filename)
    print(char_data.char_data["艾雅法拉"])
    
    res=tags_recom.recom(["狙击干员","辅助干员", "削弱", "女性干员", "治疗"])
    
    # res=tags_recom.recom(["近卫", "男", "支援"])
    print(res)
    print("="*15)
    url="https://c2cpicdw.qpic.cn/offpic_new/1224067801//39b40a48-b543-4082-986d-f29ee82645d3/0?vuin=2473990407&amp;amp;term=2"
    url="https://c2cpicdw.qpic.cn/offpic_new/391809494//857ddb74-7a0d-40ae-98db-068f8c733c86/0?vuin=2473990407&amp;amp;term=2"
    res=tags_recom.recom(images=[url])
    print(res)
    
    res2=tags_recom.char_data.get_peo_info("艾斯戴尔")
    print(res2)
    
    # st=set()
    # for name,dic in tags_recom.char_data.char_data.items():
        # st=st|set(dic['tags'])
    # print(st)
    
    

