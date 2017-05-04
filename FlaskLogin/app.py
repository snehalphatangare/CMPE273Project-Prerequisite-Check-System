import os
from uuid import uuid4
import pyautogui


from flask import Flask, request, render_template, send_from_directory,redirect, url_for, request


app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)
    

if __name__ == "__main__":
    app.run(port=4555, debug=True)
