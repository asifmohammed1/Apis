# from fastapi import FastAPI, HTTPException
import os 
import urllib.parse as up
import psycopg2
from pydantic import BaseModel
from fastapi import FastAPI, Query, APIRouter
import urllib.parse
try:
    from selenium.webdriver.common.by import By
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError:
    pass
import time
import requests
import json
from todo import *
from todo import app
import joblib
from typing import List
import wordninja
import json
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
    port=url.port,
    sslmode='require'
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
            "data":test_table.model_dump()
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

@app.get("/n8n/template")
def view_json():
    file_path = os.path.join(os.path.dirname(__file__), "n8n.json")
    with open(file_path, "r") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@chatgpt.get("/Listofmodels")
def list_of_models():
    url = "https://openrouter.ai/api/v1/models"
    response = requests.get(url, headers={})
    res = response.json()['data']
    ids = [item["id"] for item in res if "free" in item.get("id", "").lower()]
    return {"Model Names":ids}

@chatgpt.post("/Nvidia")
def openrouter_gpt(req: GptInput):
    msg = req.BOT + " **one line respond**"
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    payload = {
        "model": "moonshotai/kimi-k2-instruct",
        "messages": [
            {
                "role": "user",
                "content": msg
            }
        ],
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 4096,
        "stream": False
    }
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    res = response.json()['choices'][0]['message']['content']
    return {"Responses": res}


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
        "data":test_table.model_dump()
            }
    # except:
    #     res = {
    #         "message": "something when wrong"
    #     }
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

# Mount Todo frontend
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

@app.get("/todo", response_class=HTMLResponse)
async def todo_frontend():
    html_path = os.path.join(frontend_dir, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

app.mount("/todo/static", StaticFiles(directory=frontend_dir), name="todo-static")


# Integrate with the OpenRouter



def gptrun(message):
    msg = message + " **one line respond**"
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    payload = {
        "model": "moonshotai/kimi-k2-instruct",
        "messages": [
            {
                "role": "user",
                "content": msg
            }
        ],
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 4096,
        "stream": False
    }
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    res = response.json()['choices'][0]['message']['content']
    return res

IS_VERCEL = os.environ.get("VERCEL", "") == "1"

if not IS_VERCEL:
    from telebot.async_telebot import AsyncTeleBot
    import asyncio

    bot = AsyncTeleBot('8045583602:AAHI_Kc6RYleCjLZjtjLckbcuy6QvSAfKBQ')

    bot_task = None

    @bot.message_handler(commands=['help', 'start'])
    async def send_welcome(message):
        await bot.reply_to(message, """\
Hi there, I am Rising Star Bot.
I am excited to have a conversation with you! What can I do for you!\
""")

    @bot.message_handler(func=lambda message: True)
    async def echo_message(message):
        try:
            output = gptrun(message.text)
        except:
            output = "Due to high traffic, the bot is under maintenance. Please try again later."
        await bot.reply_to(message, output)

    async def run_bot():
        await bot.polling()

    @app.on_event("startup")
    async def startup_event():
        global bot_task
        bot_task = asyncio.create_task(run_bot())

    @app.on_event("shutdown")
    async def shutdown_event():
        bot_task.cancel()
        await bot.close_session()

@app.get("/")
async def root():
    return {"message": "Bot is running"}


