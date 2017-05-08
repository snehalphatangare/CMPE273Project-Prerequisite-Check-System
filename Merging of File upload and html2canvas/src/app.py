import os
from uuid import uuid4
import pyautogui

from flask import Flask, request, render_template, send_from_directory,redirect, url_for
import sqlite3
import time
app = Flask(__name__)
  
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


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

        print user[1]
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
    return redirect(url_for('about'))
    

@app.route('/about')
def about():
  return render_template('index.html')
  
@app.route('/ok')
def fine():
  return render_template('about.html')

@app.route('/news')
def news():
  return render_template('news.html')

@app.route('/CE')
def CE():
  return render_template('CE.html')

@app.route("/upload")

def upload():
    return render_template("upload.html")

@app.route("/uploadfile", methods=["POST"])
def uploadfile():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
            os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)
        #return render_template("button.html")

      #return send_from_directory("images", filename, as_attachment=True)
        return render_template("complete_display_image.html", image_name=filename)
      



@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

@app.route('/getmethod/<jsdata>')
def get_javascript_data(jsdata):
    print jsdata


if __name__ == '__main__':
  app.run(debug=True)
