import datetime, platform, pytz, os
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config

Config.readconfig()
Config.setpath(os.path.dirname(os.path.abspath(__file__)))
mail = MailBuilder(type = MailType.REPORT)
mail.build_body()
mail.send()

