import smtplib, platform
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class MailType:
    NOTIFY = 1
    REPORT = 2

def send_mail(send_from, send_to, subject, text, files=None, server="localhost"):

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

class MailBuilder:
    def __init__(self, send_from = 'root@tur.tancoder.com', send_to = '250224740@qq.com', type = MailType.NOTIFY):
        self.send_from = send_from
        self.send_to = send_to
        self.type = type
        self.build_subject()
        self.is_body_built = False
    
    def build_subject(self):
        if self.type == MailType.NOTIFY:
            self.subject = 'EMERGENCY Infomation From LocalBitcoin'
        elif self.type == MailType.REPORT:
            self.subject = 'Daily Report From LocalBitcoin'

    def build_body(self, text = ''):
        self.attachment = []
        if self.type == MailType.NOTIFY:
            self.body_text = 'Hi,\n\nYou need to take care of the following infomation:\n\n' + text
        elif self.type == MailType.REPORT:
            self.body_text = 'Hi,\n\nThis is the daily report from LocalBitcoin.com.'
            self.attachment.append("./output.xlsx")
        self.is_body_built = True

    def send(self):
        if self.is_body_built:
            if platform.system() == "Windows":
                print 'send mail: ', self.send_from, self.send_to, self.subject, self.body_text, self.attachment
            else:
                send_mail(self.send_from, self.send_to, self.subject, self.body_text, self.attachment)
            return True
        else:
            return False

#send_mail('root@tur.tancoder.com', '250224740@qq.com', 'A Test', 'test', ['./Vim_keys.jpg'])

