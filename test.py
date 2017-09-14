import datetime, platform
from lbcmain.mailntf import MailBuilder, MailType

mail = MailBuilder(type = MailType.REPORT)
mail.build_body()
mail.send()

print platform.system()