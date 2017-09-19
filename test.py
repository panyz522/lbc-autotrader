import datetime, platform, pytz
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor

print Monitor.get_avl_amount(1200, 1600, 12, 120, 1, 0.1)

