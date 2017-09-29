from config import Config
import os, json, datetime

class DataExplorer(object):
    """Save and read data to/from json file"""

    def __init__(self, **fileinfo):
        """Initialize DataExplorer with current status
        
        Args:
            **fileinfo: contains current file index string 'index='
        """
        self.config = Config.get_dataconfig()
        self.filename = os.path.join(self.config['path'],'doc', fileinfo['index']+'.json')
        if os.path.isfile(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = list()

    def __enter__(self):
        return self

    def __exit__(self, type, val, tb):
        self.close()

    def write_to_file(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data,f)

    def close(self):
        self.write_to_file()

    def get_field(self, *args):
        """Return specific field of data
        
        eg: get_field('USD', 'sell', 'price') return two list 
        one contains datetime object the other contains all data in item['USD']['sell'][price]"""
        datalist = list()
        timelist = list()
        for pair in self.data:
            timelist.append(datetime.datetime.strptime(pair[0],'%Y/%m/%d %H:%M:%S'))
            datalist.append(self.__getsubdic(pair[1] ,args, 0))
        return timelist, datalist

    def __getsubdic(self, dic, keys, num):
        if num >= len(keys):
            return dic
        else:
            return self.__getsubdic(dic.get(keys[num],{}), keys, num+1)

    def get_item(self, timespan = None, return_ = 'all'):
        """Get items in timespan, if no timespan specified return all items
        
        Args:
            timespan: list contains two datetime object defines items' start and end time 
            return_: 'all': get all items in timespan, 'first', 'last': get the first or last item in timespan

        Returns:
            a list contains item(s) satisfied condition
        """
        if timespan is None:
            return self.data
        datareturn = list()
        for pair in self.data:
            itemtime = datetime.datetime.strptime(pair[0], '%Y/%m/%d %H:%M:%S')
            if itemtime > timespan[1]:
                break
            if itemtime >= timespan[0]:
                lastitem = pair
                datareturn.append(pair)
                if return_ == 'first':
                    return lastitem
        if return_ == 'last':
            try:
                return lastitem
            except Exception:
                return list()
        return datareturn

    def add_item(self, itemtime, item):
        self.data.append([itemtime.strftime('%Y/%m/%d %H:%M:%S'), item])
