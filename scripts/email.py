# Code from best solution in page below:
# https://help.zoho.com/portal/community/topic/zoho-mail-servers-reject-python-smtp-module-communications

import smtplib
from os.path import basename

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr

mail_usr = 'contacto@i-perio.com'
mail_pass = 'Alejo.123'

def send_mail(subject, recipient, body, title=None, attachments=[]):
    # Define to/from
    sender_title = 'iPerio'

    # Edit html
    body = '''
<!DOCTYPE html>
<html>
    <head></head>
    <body>
        <div class="container" style="background: darkgrey; padding: 20px;">
            <div class="box" style="width: 75%; max-width: 450px; margin: auto; border-radius: 10px;
                                    box-shadow: 0px 0px 9px 3px rgba(41,41,41,.25); overflow: hidden;
                                    margin-top: 30px; font: 14px helvetica, serif;">
                <div class="title" style="background: #463F3F; padding: 5px 15px;">
                    <h1 style="color: white; font: bold 18px helvetica, serif;width: 100%;">''' + (title if title else subject) + '''</h1>
                </div>
                <div class="message" style="padding: 20px 30px; background: white; color: black;">''' + body + '''</div>
            </div>
            <div class="foot" style="text-align: center; color: white; font-size: 12px; width: 350px; margin: 10px auto 25px auto;">
                Si no deseas seguir recibiendo estos mensajes o deseas contactarte con el desarrollador, envía un correo a
                <a style="color: #463F3F; white-space: nowrap;" href="mailto:contacto@i-perio.com">contacto@i-perio.com</a>
            </div>
        </div>
    </body>
</html>
        '''

    # Create message
    msg = MIMEMultipart()
    msg['Subject'] =  Header(subject, 'utf-8')
    msg['From'] = formataddr((str(Header(sender_title, 'utf-8')), mail_usr))
    msg['To'] = recipient

    msg.attach(MIMEText(body, 'html', 'utf-8'))

    # Add image icon
    with open('resources/perio_blanco.png','rb') as img:
        msgImage = MIMEImage(img.read())
    msgImage.add_header('Content-ID', '<icono>')
    #msg.attach(msgImage)

    # Add Attachment
    for filename in attachments:
        with open(filename, 'rb') as attachment:
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attachment).read())
        # Encode the attachment
        encoders.encode_base64(payload)
        # Add payload header with filename
        payload.add_header('Content-Disposition', 'attachment', filename=basename(filename))
        msg.attach(payload)

    # Send message
    with smtplib.SMTP_SSL('smtp.zoho.com', 465) as s:
        s.login(mail_usr, mail_pass)
        s.send_message(msg)
