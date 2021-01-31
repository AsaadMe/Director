from flask import Flask , request, render_template,redirect,url_for,jsonify
import sys
import subprocess
import json
from threading import Thread

app = Flask(__name__)



#Long_wrok
def work(plink):

    res=""
    title=""
    
    title = subprocess.check_output(["youtube-dl","--get-filename", plink])
    title = str(title).replace("b'","").replace("\\n'","")
    res = subprocess.check_output(["youtube-dl","-o","static/"+title, plink])    
   
    #print("!!!!!!!!!!!!!!",res,"TITLE:",title)
       
    with open('static/result.txt','w') as file:
        file.write("{'current': 99.99, 'total': 100, 'status':'"+title+"','result': 42}")



@app.route('/' , methods=['GET', 'POST'])
def stream():

    with open('static/result.txt','w') as file:
        file.write("")
        
    
    if request.method == 'POST':
        plink = request.form['vidurl']
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