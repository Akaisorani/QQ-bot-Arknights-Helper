from os import path

import nonebot

import config

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'akaisora', 'plugins'),
        'akaisora.plugins'
    )
    nonebot.run()  
