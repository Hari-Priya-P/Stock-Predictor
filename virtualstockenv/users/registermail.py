import smtplib
import ssl
import mysql.connector
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def notify_user(user_email, user_msg):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "stockupalerts@gmail.com"  # Enter your address
    receiver_email = user_email  # Enter receiver address
    password = "stockupteam"
    msg = MIMEMultipart()
    msg['Subject'] = "Account Creation Successful!"
    msg.attach(MIMEText(user_msg, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())