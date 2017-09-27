import os, commentjson

class Config(object):
    """Set config of other class"""

    @classmethod
    def readconfig(cls):
        with open("./config.json") as file:
            cls.configs = commentjson.load(file)
    
    @classmethod
    def setpath(cls, path):
        cls.path = path

    @classmethod
    def insertpath(cls, config):
        config['path'] = cls.path
        return config

    @classmethod
    def get_monitorconfig(cls):
        return cls.insertpath(cls.configs["monitor"])

    @classmethod
    def get_mailconfig(cls):
        return cls.insertpath(cls.configs["mail"])

    @classmethod
    def get_xlsxconfig(cls):
        return cls.insertpath(cls.configs["xlsx"])

    @classmethod
    def get_dataconfig(cls):
        return cls.insertpath(cls.configs["data"])
    

