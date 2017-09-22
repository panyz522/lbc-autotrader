import datetime, platform, pytz
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config

Config.readconfig()
print Config.get_monitorconfig()

