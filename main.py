# from fastapi import FastAPI, HTTPException
import os
import urllib.parse as up
import psycopg2
from pydantic import BaseModel
from fastapi import FastAPI, Query, APIRouter
import urllib.parse
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import json
from todo import *
import joblib
from typing import List
import wordninja
# from requests_html import HTTPSession
# from webdriver_manager.chrome import ChromeDriverManager
# import google.generativeai as genai

chatgpt = APIRouter(prefix="/v1", tags=["ChatGPT"])
sql = APIRouter(prefix="/v1", tags=["SQL"])
APIs = APIRouter(prefix="/v1", tags=["API's"])
Tests = APIRouter(prefix="/v1", tags=["Test's"])
Fields = APIRouter(prefix="/v1", tags=["Fields's"])

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


@APIs.get("/read")
def read_data():
    cursor, conn = db_connect()
    cursor.execute('select * from apisec')
    data = cursor.fetchall()
    res = []
    for i in data:
        columns = [desc[0] for desc in cursor.description]
        res.append(dict(zip(columns, i)))
    return res

@APIs.post("/create")
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

@APIs.post("/getbyid")
def getbyid_data(req:int):
    cursor, conn = db_connect()
    cursor.execute(f'select * from apisec where id={req}')
    data = cursor.fetchall()
    res = []
    for i in data:
        columns = [desc[0] for desc in cursor.description]
        res.append(dict(zip(columns, i)))
    return res

@sql.get("/querybyparams")
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

@sql.post("/querybyres")
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

@APIs.get("/")
def welcome():
    return {"message":"Welcome"}

@chatgpt.post("/gemini_aistudio")
def gemini_aistudio(req: GptInput):
    model = genai.GenerativeModel(model_name='gemini-2.0-flash')
    # chat = model.start_chat()
    res = model.generate_content(req.BOT)
    return {"Responses": res.text}


@chatgpt.post("/create_logs")
def create_logs(test_table: CreateLogs):
    cursor, conn = db_connect()
    # try:
    mcc = ''.join(letter for letter in test_table.mc if letter.isalnum())
    ress = ''.join(letter for letter in test_table.res if letter.isalnum())
    title = test_table.title
    date = test_table.create_date
    title2 = test_table.title2
    mc = mcc
    res = ress
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


@chatgpt.post("/chatgpt")
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


@chatgpt.post("/chatgptv2")
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

@Tests.get("/test")
def testapi():
    return {"Responses": "Hello"}

types = {0:"str",1:"int",2:"float",3:"bool"}

@Fields.get("/FieldType")
def field_type(reqdata:str):
    model = joblib.load('Fieldsmodel')
    t = wordninja.split(reqdata)
    val = model.predict(t)[0]
    res = types[val]
    return res

@Fields.post("/predict")
def predict_faker(reqdata: str):
    model = joblib.load('fakermodel')
    count_vect = model.named_steps.vect
    r = count_vect.transform([reqdata])[0]
    val = model.named_steps.clf.predict(r)[0]
    return val


app.include_router(chatgpt)
app.include_router(sql)
app.include_router(APIs)
app.include_router(todoapis)
app.include_router(loginapis)
app.include_router(Tests)
app.include_router(Fields)
