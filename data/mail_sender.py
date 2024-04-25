import smtplib
import mimetypes
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(email, subject, text, attachments=None):
    addr_from = os.getenv('FROM')
    password = os.getenv('PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = subject

    body = text
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(os.getenv('HOST'), os.getenv('PORT'))
    server.starttls()
    server.login(addr_from, password)
    text = msg.as_string()
    server.sendmail(msg['From'], msg['To'], text)
    server.quit()
    return True
