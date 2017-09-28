import datetime, platform, pytz, os, json
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config

#Config.readconfig()
#Config.setpath(os.path.dirname(os.path.abspath(__file__)))
#mail = MailBuilder(type = MailType.REPORT)
#mail.build_body()
#mail.send()

with open("test.json", 'w') as f:
    data = {datetime.datetime(2013,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "aaa",
            datetime.datetime(2014,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "bbb",
            datetime.datetime(2011,2,4,12,0,0).strftime('%Y/%m/%d %H:%M:%S') : "ccc"}
    json.dump(data,f)

with open("test.json", 'r') as f:
    dataread = json.load(f)
    for key, value in dataread.items():
        print datetime.datetime.strptime(key, '%Y/%m/%d %H:%M:%S').year
        print value
        print ""
