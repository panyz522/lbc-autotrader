import smtplib, platform,os
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from config import Config

class MailType:
    NOTIFY = 1
    REPORT = 2



class MailBuilder:
    """MailBuilder build and send email"""
    def __init__(self, type = MailType.NOTIFY):
        self.config = Config.get_mailconfig()
        self.send_from = 'root@tur.tancoder.com'
        self.send_to = self.config["recipients"]
        self.type = type
        self.build_subject()
        self.is_body_built = False
    
    def build_subject(self):
        """Put email subject according to email type, usually don't need to directly execute"""
        if self.type == MailType.NOTIFY:
            self.subject = 'EMERGENCY Infomation From LocalBitcoin'
        elif self.type == MailType.REPORT:
            self.subject = 'Daily Report From LocalBitcoin'

    def build_body(self, text = ''):
        """Build context and attachment according to input text and mail type"""
        self.attachment = []
        if self.type == MailType.NOTIFY:
            self.body_text = 'Hi,\n\nYou need to take care of the following infomation:\n\n' + text
        elif self.type == MailType.REPORT:
            self.body_text = 'Hi,\n\nThis is the daily report from LocalBitcoin.com.'
            self.attachment.append(Config.configs['xlsx']['filename'])
        self.is_body_built = True

    def build_body_by():
        pass # TODO

    def send(self):
        """Send email if this program running on Linux or print a message"""
        if self.is_body_built:
            for recipient in self.send_to:
                if platform.system() == "Windows":
                    print 'send mail: ', self.send_from, recipient, self.subject, self.body_text, self.attachment
                else:
                    self.send_mail(self.send_from, recipient, self.subject, self.body_text, self.attachment)
            return True
        else:
            return False

    @staticmethod
    def send_mail(send_from, send_to, subject, text, files=None, server="localhost"):
        """Use smtp to send email"""
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = send_to
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            filepath = os.path.join(self.config['path'],'doc',f)
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

