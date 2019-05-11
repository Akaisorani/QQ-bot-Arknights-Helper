from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

# some comments below is from the demo code of nonebot

# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('tagrc', aliases=(), only_to_me=False)
async def tagrc(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # tags = session.get('tags', prompt='输入tag列表，空格隔开')
    tags=session.state['tags'] if 'tags' in session.state else None
    images=session.state['images'] if 'images' in session.state else None
    if not tags :return
    # 获取城市的天气预报
    tagrc_report = await get_recomm_tags(tags=tags,images=images)
    if tagrc_report is None: return 
    # 向用户发送天气预报
    await session.send(tagrc_report)

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


async def get_recomm_tags(tags: str, images: list) -> str:
    # 这里简单返回一个字符串
    # 实际应用中，这里应该调用返回真实数据的天气 API，并拼接成天气预报内容
    tags_list=tags.split()
    report=tags_recom.recom(tags_list, images)
    
    return report


from html import unescape
from lxml import html

class Character(object):
    def __init__(self):
        self.char_data=dict()
        
    def extract_all_char(self, text_string=None, text_file=None):
        if text_string is None:
            if text_file is not None:
                with open(text_file,encoding='UTF-8') as fp:
                    text_string=fp.read()
            else:
                return

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
                
class Tags_recom(object):
    def __init__(self):
        self.char_data=Character()
        self.char_data.extract_all_char(text_file="./akaisora/plugins/chardata.html")
        self.all_tags={
        '狙击', '术师', '特种', '重装', '辅助', '先锋', '医疗', '近卫',
        '减速', '输出', '生存', '群攻', '爆发', '召唤', '快速复活','费用回复',
        '新手', '治疗', '防护', '位移', '削弱', '控场', '支援',
        '近战位', '远程位',
        '近战', '远程',
        '资深干员','高级资深干员', 
        '女', '男',
        '狙击干员', '术师干员', '特种干员', '重装干员', '辅助干员', '先锋干员', '医疗干员', '近卫干员',
        '女性干员', '男性干员'
        }  
        
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
            
        # build reverse index
        char_dic=dict()
        for i in range(len(cob_lis)):
            for name in cob_lis[i][1]:
                if name not in char_dic:
                    char_dic[name]=[i]
                else:
                    char_dic[name].append(i)
        # print("")
        # print(char_dic)
        
        # remove duplicate
        min_size_id=dict()
        for name, lis in char_dic.items():
            if len(lis)>1:
                min_size_id[name]=lis[0]
                for id in lis:
                    if len(cob_lis[id][1])<len(cob_lis[min_size_id[name]][1]):
                        min_size_id[name]=id
                        
        for name, lis in char_dic.items():
            if len(lis)>1:                        
                for id in lis:
                    if id!=min_size_id[name]:
                        cob_lis[id][1].remove(name)
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        # print("")
        # for x in cob_lis:
            # print(x)
        
        #merge less rank 3
        for tags_lis, lis in cob_lis:
            cnt=0
            while len(lis)>0 and self.char_data.char_data[lis[-1]]["rank"]<="3":
                lis.pop()
                cnt+=1
            if cnt>0:
                if len(lis)>0:
                    lis.append("...{0}".format(cnt))
        cob_lis=[x for x in cob_lis if x[1]!=[]]
        
        return cob_lis
        # print("")
        # for x in cob_lis:
            # print(x)        
                
        
    
    def is_special_rm(self, cob_i):
        if set(cob_i[0])==set(["女"]):
            return True
        if set(cob_i[0])==set(["男"]):
            return True
        return False
        
    def avg_rank(self, cob_i):
        rank_map={1:0.5, 2:1, 3:3, 4:2, 5:0.5, 6:3}
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
            if tag=="高级资深干员" or tag=="资深干员":
                restags.append(tag)
            if tag=="近战" or tag=="远程":
                restags.append(tag+"位")
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
        for tag in tags:
            if tag not in self.all_tags:
                return False
        return True
    
    def recom(self, tags=None, images=None):
        if not tags:
            if images:
                tags=self.get_tags_from_image(images)
            else:
                return None
        
        if not self.check_legal_tags(tags):
            return None
        cob_lis=self.recom_tags(tags)
        if not cob_lis:
            return "没有"
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
    
    def get_tags_from_image(self, filename):
        pass

tags_recom=Tags_recom()

if __name__=="__main__":
    filename="chardata.html"
    char_data=Character()
    char_data.extract_all_char(text_file=filename)
    print(char_data.char_data["艾雅法拉"])
    
    res=tags_recom.recom(["狙击干员","辅助干员", "削弱", "女性干员", "治疗"])
    print(res)
    
    # st=set()
    # for name,dic in tags_recom.char_data.char_data.items():
        # st=st|set(dic['tags'])
    # print(st)
    
    

