from flask import Flask, render_template, request, flash
from flask.helpers import url_for
from werkzeug.utils import redirect
import requests
import json
from datetime import datetime
import time as time
import threading
import socket
import os
import psycopg2

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(12)

def connectdb():
    conn = psycopg2.connect(
    host="localhost",
    database="Monitoring",
    user="postgres",
    password="1126")
    return conn
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
    return IP

def getSites():
    db = connectdb()
    data = []
    cur = db.cursor()
    cur.execute("SELECT sitename FROM sites")
    data = cur.fetchall()
    cur.close()
    db.close()
    return data

def getCurrentTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time

def getRequest(site):
    req = requests.get(str(site))
    return req

def monitoring():
    data = getSites()
    db = connectdb()
    cur = db.cursor()
    for i in range(len(data)):
        req = getRequest(data[i][0])
        el = datetime.strptime(str(req.elapsed), "%H:%M:%S.%f")
        eltotalsecond = (el.hour*3600)+(el.minute*60)+el.second+(el.microsecond/1000000)
        jsonObj = {"el_time": str(eltotalsecond), "status_code": str(
            req.status_code), "current_time": str(getCurrentTime())}
        jsonObj = json.dumps(jsonObj, indent=4)
        cur.execute("""INSERT INTO sitedatas(datas,datasite) VALUES(%s,%s)""",(jsonObj,data[i][0],))
    db.commit()
    cur.close()
    db.close()
    print("Saved!!")

@app.route("/home")
def home():
    data = getSites()
    return render_template('home.html', data=data, len=len(data))
    #return render_template('home.html', data=data, len=len(data), eltime=request.args.get('eltime'),
    #                       statuscode=request.args.get('statuscode'), currenttime=request.args.get('currenttime'))

@app.route("/plot", methods=['POST'])
def plotting():
    plot_str = request.form['plot_str']
    data_eltime = []
    data_statuscode = []
    data_currenttime = []

    db = connectdb()
    cur = db.cursor()
    cur.execute("""SELECT datas FROM sitedatas WHERE datasite=%s""",(plot_str,))
    data_x = cur.fetchall()
    for item in data_x:
        data_eltime.append(float(item[0]['el_time']))
        data_statuscode.append(int(item[0]['status_code']))
        data_currenttime.append(item[0]['current_time'])
    cur.close()
    db.close()
    try:
        return render_template("home.html",data=getSites(),
                            len=len(getSites()), eltime=data_eltime, statuscode=data_statuscode,
                            currenttime=data_currenttime, plot_title = plot_str)
    except:
        return redirect("/home")

@app.route("/add", methods=['POST'])
def addSites():
    site = request.form['adding']
    try:
        requests.get(site)
    except:
        flash("The given site does not exist or is not accessible.")
        return redirect("/home")
    db = connectdb()
    cur = db.cursor()
    cur.execute("""INSERT INTO sites(sitename)
             VALUES(%s);""", (str(site),))
    db.commit()
    cur.close()
    db.close()
    flash("Site added successfully.")
    return redirect("/home")

@app.route("/delete", methods=['POST'])
def deleteSites():
    selected = request.form['delete']
    db = connectdb()
    cur = db.cursor()
    try:
        cur.execute("""DELETE FROM sites WHERE sites.sitename=%s""", (selected,))
        cur.execute("""DELETE FROM sitedatas WHERE sitedatas.datasite=%s""",(selected,))
        db.commit()
        cur.close()
        db.close()
        flash("The site has been deleted.")
        return redirect("/home")
    except:
        cur.close()
        db.close()
        flash("The site couldn't be deleted.")
        return redirect("/home")


if(__name__ == '__main__'):
    app.run(host=str(get_ip()),port=5000,debug=True)

#timerStart = threading.Thread(target=timer)
#timerStart.start()
