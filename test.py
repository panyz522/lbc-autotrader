import datetime, platform, pytz, os, json
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config
from lbcmain.dataexplorer import DataExplorer

Config.readconfig()
Config.setpath(os.path.dirname(os.path.abspath(__file__)))


#mail = MailBuilder(type = MailType.REPORT)
#mail.build_body()
#mail.send()

#with open("test.json", 'w') as f:
#    data = {datetime.datetime(2013,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "aaa",
#            datetime.datetime(2014,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "bbb",
#            datetime.datetime(2011,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "ccc"}
#    json.dump(data,f)

#with open("test.json", 'r') as f:
#    dataread = json.load(f)
#    for key, value in dataread.items():
#        print datetime.datetime.strptime(key, '%Y/%m/%d %H:%M:%S').year
#        print value
#        print ""

with DataExplorer(index = 'index') as dataexp:
    dataexp.add_item(datetime.datetime(2016,3,4,1,2,3), {'key1':{'key1.1':123}, 'key2':'value2','key3':123})
    dataexp.add_item(datetime.datetime(2017,3,4,1,2,3), {'key1':{'key1.1':456}, 'key2':'eee','key3':1.222})
    dataexp.add_item(datetime.datetime(2018,3,4,1,2,3), {'key1':{'key1.1':789}, 'key2':'ddd','key3':1})
with DataExplorer(index = 'index') as dataexp:
    items = dataexp.get_item([datetime.datetime(2012,9,1), datetime.datetime(2015,1,1)], 'all')
    print items
    timelist, datalist = dataexp.get_field('key1', 'key1.1')
    print timelist
    print datalist

#with open('test.json', 'w') as f:
#    json.dump([('aaa', {'adf':'ddd'}),('bbb', {'c':'d'})],f)
