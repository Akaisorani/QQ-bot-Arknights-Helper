import os

class Record(object):
    def __init__(self, filename, writecnt=10):
        self.filename=filename
        self.cnt=0
        self.writecnt=writecnt
        self.obj=None

        if os.path.exists(filename):
            self.load()
        else:
            self.obj=dict()
            self.dump()
        

    def update(self, obj):
        self.obj=obj
        
    def count(self, num=1):
        self.cnt+=num
        if self.cnt>=self.writecnt:
            self.cnt=0
            self.dump()

    def dump(self):
        with open(self.filename, "w") as fp:
            fp.write(repr(self.obj))

    def load(self):
        with open(self.filename, "r") as fp:
            self.obj=eval(fp.read())
        return self.obj

    def get(self):
        return self.obj 

    def add(self, pathname, num=1):
        pathname=pathname.split("/")
        path=pathname[:-1]
        name=pathname[-1]
        ob=self.obj
        for typ in path:
            if typ not in ob:
                ob[typ]=dict()
            ob=ob[typ]
        if name not in ob: ob[name]=num
        else: ob[name]+=num
        self.count()      
    
