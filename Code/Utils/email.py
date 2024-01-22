import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import cv2

def sendPicEmail(block,frame):
    print('\nEmail script start')
    #frame = cv2.flip(frame,-1)
    #Define time stamp and capture image
    pic_time = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = pic_time + '.jpg'
    cv2.imwrite(filename,frame)
    #Email info(Sender)
    smtpUser = 'hamza809t@gmail.com'
    smtpPass = 'apjdihlaoqrqaaew'

    #Destination email info
    #toAdd = 'shahkhanhamzahsk@gmail.com'
    toAdd = ['enpm809ts19@gmail.com','shahkhanhamzahsk@gmail.com']#,'rpatil10@umd.edu']
    fromAdd = smtpUser
    subject = 'Object Retrived'
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = fromAdd
    #msg['To'] = toAdd
    msg['To'] = ','.join(toAdd)
    #msg['Cc'] = 'shahkhanhamzahsk@gmail.com'
    msg.preamble = 'Image recorded at ' + pic_time

    #Email text
    body = MIMEText('\nUser: Hamza Shah Khan (hamzask@umd.edu) \nThe '+block+' Block has been retrived successfully at ' + pic_time)
    msg.attach(body)

    #Attachment
    fp = open(filename,'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)

    msg.attach(img)

    #Send Email
    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser,smtpPass)
    s.sendmail(fromAdd, toAdd, msg.as_string())
    s.quit()

    print(f'{block} Grabbed: Email delivered!')
