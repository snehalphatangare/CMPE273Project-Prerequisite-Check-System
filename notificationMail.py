import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

 
 
fromaddr = "abhishek.up25@gmail.com"
toaddr = "abhishek.upadhyay@sjsu.edu"
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "Enrollment Eligibility"
 
body = "You Are Enrolled Successfully"
msg.attach(MIMEText(body, 'plain'))
 
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "********")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()