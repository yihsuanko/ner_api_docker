from typing import Optional, List, Union
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from app.ner_predict import *
from pydantic import BaseModel, parse_obj_as

TOKEN = "albert_base_chinese_ner_0329"
MODEL = "albert_base_chinese_ner_0329"

app = FastAPI()
templates = Jinja2Templates(directory="./app/templates")

class Input(BaseModel):
    id: int
    sentence: str

class Result(BaseModel):
    entity_group: str
    score: float
    word: str
    start: int
    end: int

class Result_Output(BaseModel):
    id: int
    content: List[Result]

class Output(BaseModel):
    result: List[Result_Output]


@app.post("/", response_model=Output)
def result(input: List[Input]):

    result = []
    for data in input:
        temp = {"id":data.id}
        content = data.sentence
        content = content.replace(" ","[MASK]")    
        document = pred_result(TOKEN, MODEL, content)
        temp["content"] = document
        result.append(temp)

    print(result)
    return {"result": result}


@app.get("/")
def read_root(request: Request, content="", result=""):

    if content != "":
        content = content.replace(" ","[MASK]")
        result = pred_result(TOKEN, MODEL, content)

    response = {
        "request": request,
        "content": content,
        "result": result,
    }
    return templates.TemplateResponse("home.html", response)
