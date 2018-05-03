# coding:utf-8
"""PDF interface module"""
import smtplib
import time

from email.header import Header
from email.mime.text import MIMEText
import traceback

from jinja2 import Environment, PackageLoader

from config import CFG as O_O


def send_email(subject, receivers, template_path, **values):
    """public email function."""
    env = Environment(loader=PackageLoader('workers', 'templates'))

    template = env.get_template(template_path)
    content = template.render(**values)
    sender = 'mail@lazor.cn'

    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = f'Wondershare eSign+ <{sender}>'
    message['To'] = ','.join(receivers)
    message['subject'] = Header(subject, 'utf-8')
    message['Accept-Language'] = 'zh-CN'
    message['Accept-Charset'] = 'ISO-8859-1, utf-8'

    for _ in range(5):
        try:
            smtp_obj = smtplib.SMTP()
            smtp_obj.connect(O_O.mail.host, 25)
            smtp_obj.login(O_O.mail.user, O_O.mail.pswd)
            smtp_obj.sendmail(sender, receivers, message.as_string())
            smtp_obj.quit()
            break
        except ConnectionRefusedError as exception:
            traceback.print_exc()
            return dict(
                result=0,
                status=1,
                msg='Connection refused when sending email.',
                exc_doc=str(exception))
        except TimeoutError as exception:
            return dict(
                result=0,
                status=1,
                msg='Connect email server time out.',
                data=dict(
                    exc_doc=str(exception),
                    output_html=content))
        time.sleep(1)

    return dict(
        result=1,
        status=0,
        msg='Send email successfully.',
        data=values)
