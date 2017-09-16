import datetime, platform, pytz
from lbcmain.mailntf import MailBuilder, MailType
dt_bj = datetime.datetime(2017, 1, 1, 1, 0, tzinfo = pytz.timezone('Asia/Shanghai'))
dt_now = datetime.datetime.utcnow()
print dt_now
dt_utc = datetime.datetime.combine(dt_now.date(), dt_bj.astimezone(pytz.utc).time())
if dt_now >= dt_utc:
    report_time = dt_utc + datetime.timedelta(days = 1)
else:
    report_time = dt_utc
print report_time