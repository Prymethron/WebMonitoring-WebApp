import psycopg2
from datetime import datetime
import requests
import json
from config import config
from prefect import task, Flow
from datetime import timedelta
from prefect.schedules import IntervalSchedule
from configparser import ConfigParser

def connectdb(): #connect to database
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return conn
    
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

def Counter(filename='database.ini', section='counter'):
    config = ConfigParser()
    config.read(filename)
    params = config.items(section)
    count = int(params[0][1])
    if(count == 24):
        count = 0
        config.set(section,'count',str(count))
        with open(filename,'w') as configfile:
            config.write(configfile)
        return True
    config.set(section,'count',str(count+1))
    with open(filename,'w') as configfile:
        config.write(configfile)
    return False
    

@task
def monitoring():
    data = getSites()
    db = connectdb()
    cur = db.cursor()
    if(Counter()):
        cur.execute(
            """TRUNCATE sitedatas""")
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

schedule = IntervalSchedule(interval=timedelta(hours=1))
with Flow("Monitorizing", schedule) as flow:
    monitoring()

flow.run()




