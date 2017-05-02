import os
from uuid import uuid4
import pyautogui


from flask import Flask, request, render_template, send_from_directory


app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("upload.html")
def homepage():
    return """
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>Using an existing canvas to draw on</title>
    <style>
        canvas {
            border: 1px solid black;
        }
        button {
            clear: both;
            display: block;
        }
        #content {
            background: rgba(100, 255, 255, 0.5);
            padding: 50px 10px;
        }
    </style>
</head>
<body>
<div><h1>Take the screenshot and Enjoy</h1>
    <div id="content">Hello Shraddha , Welcome to San Francisco</div>
</div>

<script type="text/javascript" src="../dist/html2canvas.js"></script>
<button>Run html2canvas</button>
<script type="text/javascript">
    var canvas = document.querySelector("canvas");
    var ctx = canvas.getContext("2d");


    document.querySelector("button").addEventListener("click", function() {
        html2canvas(document.querySelector("#content"), {canvas: canvas}).then(function(canvas) {
            //console.log('Drew on the existing canvas');
        });
    }, false);

</script>
</body>
</html>

"""

@app.route("/upload", methods=["POST"])
def upload():
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

    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete_display_image.html", image_name=filename)
   



@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)




if __name__ == "__main__":
    app.run(port=4555, debug=True)
