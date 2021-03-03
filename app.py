from flask import Flask , request, render_template
from threading import Thread
import youtube_dl
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("secret")
socketio = SocketIO(app)

user_sess = {}

@socketio.on('bg-job')
def handle_json(message):

    if (vidurl := message.get('vidurl')) != None:

        with youtube_dl.YoutubeDL({'outtmpl': '%(title)s.%(ext)s'}) as ydl:
            filename = ydl.extract_info(vidurl, download=False)['title']

        if filename in user_sess:
            ext = '.' + user_sess[filename]['ext']
            if float(user_sess[filename]['percent']) > 99:
                resp = {"current": 99.99, "total": 100, "status":filename + ext, "result":42, "finished":"True", "size":user_sess[filename]['size']}
                emit('response',resp)
            else:
                resp = {"current": user_sess[filename]['percent'], "total": 100, "status":filename + ext, "result":42}
                emit('response',resp)

def hook(d):

    global user_sess 
    filename = d['filename'].replace("static/","").strip().split('.')[0]
    if filename not in user_sess:
        user_sess[filename] = {'ext':'', 'size':0, 'percent':0}

    user_sess[filename]['ext'] = d['filename'].replace("static/","").strip().split('.')[1]

    if d['status'] == 'finished': 
        user_sess[filename]['size'] = d["_total_bytes_str"]

    if d['status'] == 'downloading': 
        user_sess[filename]['percent'] = d['_percent_str'].replace('%','').strip()

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