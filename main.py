from fastapi import FastAPI, HTTPException
import os
import urllib.parse as up
import psycopg2
from pydantic import BaseModel
from fastapi import FastAPI, Query
import urllib.parse
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
# from requests_html import HTTPSession
# from webdriver_manager.chrome import ChromeDriverManager

def db_connect():
    up.uses_netloc.append("postgres")
    url = up.urlparse("postgres://sonuasif748:jBYaXx0NqOh8@ep-white-rain-379558.ap-southeast-1.aws.neon.tech/neondb")
    conn = psycopg2.connect(database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
    )
    cursor = conn.cursor()
    return cursor, conn


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateData(BaseModel):
    name:str
    number:int
    description:str

class CreateLogs(BaseModel):
    title:str
    title2:str
    create_date:str
    mc:str
    res:str

class Queryenter(BaseModel):
    querystatement:str

class GptInput(BaseModel):
    BOT:str


@app.get("/read")
def read_data():
    cursor, conn = db_connect()
    cursor.execute('select * from apisec')
    data = cursor.fetchall()
    res = []
    for i in data:
        columns = [desc[0] for desc in cursor.description]
        res.append(dict(zip(columns, i)))
    return res

@app.post("/create")
def create_data(test_table: CreateData):
    cursor, conn = db_connect()
    try:
        name = test_table.name
        description = test_table.description
        cursor.execute(f"INSERT INTO apisec (name, number, description) VALUES ('{name}', {test_table.number}, '{description}')")
        conn.commit()
        res = {
            "message": "data created successfully",
            "status":201,
            "data":dict(test_table)
                }
    except:
        res = {
            "message": "something when wrong"
        }
    return res

@app.post("/getbyid")
def getbyid_data(req:int):
    cursor, conn = db_connect()
    cursor.execute(f'select * from apisec where id={req}')
    data = cursor.fetchall()
    res = []
    for i in data:
        columns = [desc[0] for desc in cursor.description]
        res.append(dict(zip(columns, i)))
    return res

@app.get("/querybyparams")
def querybyparams_data(params:str = Query(None)):
    cursor, conn = db_connect()
    try:
        cursor.execute(params)
        conn.commit()
        data = cursor.fetchall()
        if data:
            res = []
            for i in data:
                columns = [desc[0] for desc in cursor.description]
                res.append(dict(zip(columns, i)))
            data = res
        else:
            data = {}
    except:
        conn.commit()
        data = "Invaild Query"
    return {"message":"query what you have enter is applied","data":data}

@app.post("/querybyres")
def querybyres_data(q:Queryenter):
    cursor, conn = db_connect()
    try:
        cursor.execute(q.querystatement)
        conn.commit()
        data = cursor.fetchall()
        if data:
            res = []
            for i in data:
                columns = [desc[0] for desc in cursor.description]
                res.append(dict(zip(columns, i)))
            data = res
    except:
        conn.commit()
        data = "Invaild Query"
    return {"message": "query what you have enter is applied", "data": data}

@app.get("/")
def welcome():
    return {"message":"Welcome"}


# @app.post("/chatgpt4")
# def chat_gpt4(input_text:GptInput):
#     params = {'q': input_text.BOT}
#     query_string = urllib.parse.urlencode(params)
#     BaseURL = f"https://googpt.ai/?{query_string}&hl=en"
#     # page = requests.get(BaseURL).text
#     # soup = BeautifulSoup(page, 'html.parser')
#     # soup_alt = BeautifulSoup(page, 'html.parser')
#     # element = soup.find('div', {'class': 'chatgpt-result'})
#     # res = element.text
#     # obj1 = ChromeDriverManager()
#     # path = obj1.install()
#     s = HTTPSession()
#     options = Options()
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     driver = webdriver.Chrome(options=options)
#     # driver = webdriver.Chrome()
#     driver.get(BaseURL)
#     time.sleep(10)
#     driver.implicitly_wait(10)
#     res = driver.find_element(By.XPATH, '//*[@class="chatgpt-result"]').text
#     return {"data":res}


@app.post("/create_logs")
def create_logs(test_table: CreateLogs):
    cursor, conn = db_connect()
    # try:
    mcc = ''.join(letter for letter in test_table.mc if letter.isalnum())
    title = test_table.title
    date = test_table.create_date
    title2 = test_table.title2
    mc = mcc
    res = test_table.res
    cursor.execute(f"INSERT INTO logs (title,title2, create_date,mc, res) VALUES ('{title}','{title2}', '{date}', '{mc}', '{res}')")
    conn.commit()
    res = {
        "message": "data created successfully",
        "status":201,
        "data":dict(test_table)
            }
    # except:
    #     res = {
    #         "message": "something when wrong"
    #     }
    return res


@app.post("/chatgpt")
def chat_gpt(input_text:GptInput):
    try:
        pload = json.dumps({
    "prompt": input_text.BOT,
    "conversation": 1
    })
        headers = {
    'Content-Type': 'application/json',
    }
        r = requests.post('https://www.catgpt.dog/complete', data=pload, headers=headers)
        res = {"Response":json.loads(r.text)['completion']}
    except:
        res = {"Response":"Sorry, we're experiencing high traffic and our GPUs are currently overloaded. Please try again later. Thank you for your understanding"}
    return res  


@app.post("/chatgptv2")
def chat_gptv2(input_text:GptInput):
    try:
        replace = {"Meow!":"Hey!","Meow":"Hey","meon":"hey","pur":"thank you","purr":"thank you","growl":"howl","pur-fect":"perfect",
                "meow-meow":"hey","Me-ow!":"Hey!","Me-ow":"Hey","prrr":"","prrrr":"","me-ow":"hey", "Purr...":"","Purr.":"",
                "pur":"","Purrr.":"","Purr.":"","Prrrr...":"", "Meow,":"Hey,","Purr.":""}
        pload = json.dumps({
    "prompt": input_text.BOT,
    "conversation": 1
    })
        headers = {
    'Content-Type': 'application/json',
    }
        r = requests.post('https://www.catgpt.dog/complete', data=pload, headers=headers)
        txt = json.loads(r.text)['completion']
        for k,v in replace.items():
            txt = txt.replace(k,v)
        res = {"Response":txt}
    except:
        res = {"Response":"Sorry, we're experiencing high traffic and our GPUs are currently overloaded. Please try again later. Thank you for your understanding"}
    return res  

