import smtplib
import sqlite3

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


# Connecting to the database file
conn = sqlite3.connect('/Users/Abhishek/SQLiteDB/CheckSyatemDB.sqlite')
c = conn.cursor()

c.execute('SELECT * FROM emailDB')

dbRecordTuple = c.fetchone()
emailId = dbRecordTuple[0]
print emailId




 
##check systems email id is fetched from email.properties file
checkSystemEmailAddr = dbRecordTuple[0]
checkSystemEmailPwd = dbRecordTuple[1]

##student's email id to be fetched from his login session request
toaddr = "abhishek.upadhyay@sjsu.edu"
msg = MIMEMultipart()
msg['From'] = checkSystemEmailAddr
msg['To'] = toaddr
msg['Subject'] = "Prerequisite Check Sytem"


##fetching this flag from DB for that particular student
enrollmentFlag = True

if(enrollmentFlag):
    body = "You Are Enrolled Successfully"
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(checkSystemEmailAddr, checkSystemEmailPwd)
    text = msg.as_string()
    server.sendmail(checkSystemEmailAddr, toaddr, text)
    server.quit()

# Committing changes and closing the connection to the database file
conn.commit()
conn.close()


