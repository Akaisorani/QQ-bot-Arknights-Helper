from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot import Message, MessageSegment

import os, sys
import requests
from lxml import html

import subprocess

o_path = os.getcwd()
sys.path.append(o_path)
o_path=o_path+"/akaisora/plugins/"
sys.path.append(o_path)

from tuchuang import Jd_tuchuang

path_prefix="./akaisora/plugins/"

# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('checklog', aliases=(), only_to_me=True)
async def checklog(session: CommandSession):
    num_lines=session.state['num_lines'] if 'num_lines' in session.state else 28
    report = await checknohup(num_lines=num_lines)
    if not report: return
    await session.send(report)

@checklog.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()
    
    print("stripped_arg", stripped_arg)
    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg and stripped_arg.isdigit():
            session.state['num_lines'] = int(stripped_arg)
        return

async def checknohup(num_lines) -> str:
    try:
        logfile="./nohup.out"
        report=tail(logfile, num_lines)
    except Exception as e:
        print(e)
        report="error"
    if not report: report="error"
    
    return report

def tail(filename, n):
    lines = subprocess.getoutput('tail -n '+str(n)+" "+filename)
    return lines


if __name__=="__main__":
    res=tail("./akaisora/plugins/checklog.py", 28)
    print(res)

    
    

