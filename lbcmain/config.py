import os, commentjson

class Config(object):
    """Set config of other class"""
    @classmethod
    def readconfig(cls):
        with open("./config.json") as file:
            cls.configs = commentjson.load(file)

    @classmethod
    def get_monitorconfig(cls):
        return cls.configs["monitor"]

    @classmethod
    def get_mailconfig(cls):
        return cls.configs["mail"]
