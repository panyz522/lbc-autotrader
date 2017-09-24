import datetime, platform, pytz
from lbcmain.mailntf import MailBuilder, MailType
from lbcmain.lbcmonitor import Monitor
from lbcmain.config import Config

Config.readconfig()
mail = MailBuilder(type = MailType.REPORT)
mail.build_body()
mail.send()

