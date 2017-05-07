
from flask import Flask, render_template, request,redirect, url_for
import sqlite3
import time
app = Flask(__name__)

@app.route('/checklogin')
def log():
  #return render_template('check.html')
  return "Try more"
  

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user=username.split("@")
        conn = sqlite3.connect('/Users/shraddhayeole/Desktop/Sithu/sithuproject/login.sqlite')
        c = conn.cursor()
        c.execute('SELECT * FROM login')
        print "successful"
        rows = c.fetchall()
        print rows
        recordfounf='false'
        for row in rows:
            dbUser = row[0]
            dbPass = row[1]
            print dbUser
            print dbPass
            if username in dbUser:
                if password in dbPass:
                    recordfounf='true'
                    print recordfounf
                    break
                        
        if recordfounf=='false':
            
            print "invalid user"

        
        print recordfounf
        if user[1] == 'sjsu.edu' and recordfounf=='true':
            return redirect(url_for('secret'))
            
            #return redirect(url_for('log'))
        else:
            error = 'Invalid Credentials. Please try again.'
            #time.sleep(10)
            #return redirect(url_for('login'))
    return render_template('login.html', error=error)

@app.route('/secret')
def secret():
    return "You have successfully logged in"
    








if __name__ == '__main__':
   app.run(debug = True)
