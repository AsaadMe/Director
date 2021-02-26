from flask import Flask , request, render_template
from threading import Thread
import youtube_dl
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("secret")
socketio = SocketIO(app)

percent = "0"
filename = ""
size = ""

@socketio.on('bg-job')
def handle_json(message):
    global percent
    global filename
    global size
    
    if float(percent) > 99:
        resp = {"current": 99.99, "total": 100, "status":filename, "result":42, "finished":"True", "size":size}
        emit('response',resp)
    else:
        resp = {"current": percent, "total": 100, "status":filename, "result":42}
        emit('response',resp)

def hook(d):
    global filename 
    filename = d['filename'].replace("static/","").strip()
    if d['status'] == 'finished':
        global size 
        size = d["_total_bytes_str"]

    if d['status'] == 'downloading':
        global percent 
        percent = d['_percent_str'].replace('%','').strip()


#Long_wrok
def work(plink):

    ydl_opts = {
    'outtmpl': 'static/%(title)s.%(ext)s',
    'format':'22/best',
    'restrict-filenames':True,
    'noplaylist': True,
    'progress_hooks': [hook]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([plink])
   
       

@app.route('/' , methods=['GET', 'POST'])
def stream():
            
    if request.method == 'POST':
        plink = request.form['vidurl']

        thread = Thread(target=work,args=(plink,))
        thread.daemon = True
        thread.start()
        return render_template('index.html')
    if request.method == 'GET':
        return render_template('index.html')

 
if __name__ == '__main__':
    socketio.run(app,debug=True)