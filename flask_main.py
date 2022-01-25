from flask import Flask, render_template, request, flash
from werkzeug.utils import redirect
import requests
from datetime import datetime
import socket
import os
import psycopg2
import validators
from config import config

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(12)


def connectdb(): #connect to database
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn


def get_ip():  # get auto ip so all devices at the same LAN can access to the site
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
    return IP

def getSites(): # get sites from db
    db = connectdb()
    data = []
    cur = db.cursor()
    cur.execute("SELECT sitename FROM sites")
    data = cur.fetchall()
    cur.close()
    db.close()
    return data

def splitted(data): #split site names 
    datasplitted = []
    for x in data:
        if(x[0][:8] == "https://"):
            if(x[0][len(x[0])-1:]=='/'):
                datasplitted.append(x[0][8:len(x[0])-1])
            else:
                datasplitted.append(x[0][8:])
    return datasplitted

def getImgurl(): # get image urls from db
    db = connectdb()
    data = []
    cur = db.cursor()
    cur.execute("SELECT imgurl FROM sites")
    data = cur.fetchall()
    cur.close()
    db.close()
    return data

def is_url_image(image_url): #Checks if the given string is url and image
    if(validators.url(image_url)):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
    return False


def getCurrentTime(): # get curren time
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time


def getRequest(site): # Send request to a site
    req = requests.get(str(site))
    return req


@app.route("/home") # homepage of the website
def home():
    data = getSites()
    return render_template('home.html', data=data, len=len(data), splitted=splitted(data), imgurl=getImgurl())
    # return render_template('home.html', data=data, len=len(data), eltime=request.args.get('eltime'),
    #                       statuscode=request.args.get('statuscode'), currenttime=request.args.get('currenttime'))


@app.route("/plot", methods=['POST']) # plotting datas
def plotting():
    plot_str = request.form['plot_str']
    data_eltime = []
    data_statuscode = []
    data_currenttime = []

    db = connectdb()
    cur = db.cursor()
    cur.execute("""SELECT datas FROM sitedatas WHERE datasite=%s""", (plot_str,))
    data_x = cur.fetchall()
    for item in data_x:
        data_eltime.append(float(item[0]['el_time']))
        data_statuscode.append(int(item[0]['status_code']))
        data_currenttime.append(item[0]['current_time'])
    cur.close()
    db.close()
    try:
        return render_template("home.html", data=getSites(), splitted=splitted(getSites()), imgurl=getImgurl(),
                               len=len(getSites()), eltime=data_eltime, statuscode=data_statuscode,
                               currenttime=data_currenttime, plot_title=plot_str)
    except:
        return redirect("/home")


@app.route("/adding", methods=['GET']) 
def routeToAdd():
    return render_template('add.html')


@app.route("/add", methods=['POST'])
def addSites():
    site = request.form['adding']
    imgurl = request.form['addingImage']
    try:
        requests.get(site)
    except:
        flash("The given site does not exist or is not accessible.")
        return redirect("/home")
    db = connectdb()
    cur = db.cursor()
    if (is_url_image(imgurl)):
        pass
    else:
        imgurl = "https://kariyer.ariteknokent.com.tr/Content/img/default-logo.png"
        
    cur.execute("""INSERT INTO sites(sitename,imgurl)
             VALUES(%s,%s);""", (str(site), str(imgurl)))
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
        cur.execute(
            """DELETE FROM sites WHERE sites.sitename=%s""", (selected,))
        cur.execute(
            """DELETE FROM sitedatas WHERE sitedatas.datasite=%s""", (selected,))
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
    app.run(host=str(get_ip()), port=5000, debug=True)
    