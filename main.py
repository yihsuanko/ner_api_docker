from typing import Optional
import spacy
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from app.ner_predict import *
from pydantic import BaseModel

TOKEN = "albert_base_chinese_ner_0329"
MODEL = "albert_base_chinese_ner_0329"
en_core_web_lg = spacy.load("en_core_web_lg")

app = FastAPI()
templates = Jinja2Templates(directory="./app/templates")

class Input(BaseModel):
    sentence: str

class Extraction(BaseModel):
    first_index: int
    last_index: int
    name: str
    content: str

class Output(BaseModel):
    extractions: List[Extraction]

@app.post("/extractions", response_model=Output)
def extractions(input: Input):
    document = en_core_web_lg(input.sentence)

    extractions = []
    for entity in document.ents:
        extraction = {}
        extraction["first_index"] = entity.start_char
        extraction["last_index"] = entity.end_char
        extraction["name"] = entity.label_
        extraction["content"] = entity.text
        extractions.append(extraction)

    return {"extractions": extractions}

class Result(BaseModel):
    entity_group: str
    score: float
    word: str
    start: int
    end: int

class Result_Output(BaseModel):
    result: List[Result]

@app.post("/", response_model=Result_Output)
def result(input: Input):
    content = input.sentence
    content = content.replace(" ","[MASK]")    
    document = pred_result(TOKEN, MODEL, content)
    result = []
    for i in document:
        result.append(i)

    return {"result": result}


@app.get("/")
def read_root(request: Request, content="", result=""): #, MODEL, TOKEN, content="", result=""

    if content != "":
        content = content.replace(" ","[MASK]")
        result = pred_result(TOKEN, MODEL, content)

    response = {
        "request": request,
        "content": content,
        "result": result,
    }
    return templates.TemplateResponse("home.html", response)
