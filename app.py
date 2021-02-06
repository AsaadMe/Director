from flask import Flask , request, render_template,redirect,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from threading import Thread
import youtube_dl
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    url_history = db.Column(db.String())    
    
    def __init__(self, url_history):
        self.url_history = url_history


def hook(d):
    filename = d['filename'].replace("static/","").strip()
    if d['status'] == 'finished':
        with open('static/result.txt','w') as file:
            file.write("{'current': 99.99, 'total': 100, 'status':'" + filename + "','result': 42 , 'finished':'True'}")
    if d['status'] == 'downloading':
        percent = d['_percent_str'].replace('%','').strip()
        with open('static/result.txt','w') as file:
            file.write("{'current':" + percent + ", 'total': 100, 'status':'" + filename + "','result': 42}")

#Long_wrok
def work(plink):

    ydl_opts = {
    'outtmpl': 'static/%(title)s.%(ext)s',
    'progress_hooks': [hook]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([plink])
   
       


@app.route('/' , methods=['GET', 'POST'])
def stream():

    with open('static/result.txt','w') as file:
        file.write("")
        
    
    if request.method == 'POST':
        plink = request.form['vidurl']

        data = History(url_history=str(plink))
        db.session.add(data)
        db.session.commit()

        thread = Thread(target=work,args=(plink,))
        thread.daemon = True
        thread.start()
        return render_template('index.html')
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/status')
def taskstatus():

    data = ""
    with open('static/result.txt','r') as file:
        data = file.read()
        if data !="":
            response = json.loads(data.replace("'","\""))
            return response
        else:
            return {
            'state': 'PENDING',
            'current': 10,
            'total': 100,
            'status': 'Pending...'
        }
 
 
if __name__ == '__main__':
    app.run(threaded=True)