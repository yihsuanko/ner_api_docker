# NER Docker

使用 [Hugging Face Hub](https://huggingface.co/models) 之前訓練好的模型來製作api和docker映像檔。

- [程式建置流程](#程式建置流程)
- [程式說明](#程式說明)
   - [FASTAPI](#FASTAPI)
   - [postman](#postman)
   - [pipelines](#pipelines)
   - [docker](#docker)

## 程式建置流程
- 透過FASTAPI 來製作 get/post api
- 使用postman測試post api
- 使用Jinja2來製作HTML template
- 使用transformers pipelines 來進行模型預測
- 使用docker製作映像檔

## 程式說明

### [FASTAPI](https://fastapi.tiangolo.com/)
- installation
    - pip install fastapi
    - pip install "uvicorn[standard]"
    - pip install jinja2
- Run the code
    - uvicorn main:app --reload
- api 用途
    - POST: to create data.
    - GET: to read data.
    - PUT: to update data.
    - DELETE: to delete data.

#### get api
- URL:`/`
- method:`get`
- Headers:
    - `Content-Type`: `text/html; charset=utf-8`
- code:
```python
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from app.ner_predict import *

app = FastAPI()
templates = Jinja2Templates(directory="./app/templates")
@app.get("/")
def read_root(request: Request, content="", result=""):

    if content != "":
        document = content.replace(" ", "[MASK]")
        document = content.replace("　", "[MASK]")
        result = get_result(TOKEN, MODEL, document)

    response = {
        "request": request,
        "content": content,
        "result": result,
    }
    return templates.TemplateResponse("home.html", response)
```

#### post api
- URL: `/api/ner`
- Method: `POST`
- Headers:
    - `Content-Type`: `application/json`
    - `accept`: `application/json`
- Example Request Body:
    ```
    [
        {
            "id": 0,
            "sentence": "三峽親友及校園案40例最多"
        }
    ]
    ```
- Example Request:
    ```
    curl -X 'POST' \
        'http://127.0.0.1:8000/api/ner' \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        -d '[
        {
            "id": 0,
            "sentence": "三峽親友及校園案40例最多"
        }
    ]'
    ```
- Example Succcess Response:
```
    {
        "result": [
            {
            "id": 0,
            "content": [
                {
                "entity_group": "ORG",
                "score": 0.9293190240859985,
                "word": "三峽",
                "start": 0,
                "end": 2
                }
            ]
            }
        ]
    }
```
- code:
```python
from fastapi import FastAPI, Request
from app.ner_predict import *
from pydantic import BaseModel

TOKEN = "albert_base_chinese_ner_0329"
MODEL = "albert_base_chinese_ner_0329"

app = FastAPI()

class Input(BaseModel):
    id: int
    sentence: str


class Result(BaseModel):
    entity_group: str
    score: float
    word: str
    start: int
    end: int


class ResultOutput(BaseModel):
    id: int
    content: List[Result]


class Output(BaseModel):
    result: List[ResultOutput]


@app.post("/api/ner", response_model=Output)
def result(input: List[Input]):

    result = []
    for data in input:
        temp = {"id": data.id}
        content = data.sentence
        document = content.replace(" ", "[MASK]")
        document = pred_result(TOKEN, MODEL, document)
        temp["content"] = document
        result.append(temp)

    print(result)
    return {"result": result}
```

### [postman](https://www.postman.com/)
- 由於直接輸入網址獲取資料屬於get方法，因此無法檢視post api以下有兩個辦法可以檢視post api
- FASTAPI內建的 /doc
run fast api 之後在網址上
    1. 輸入`http://127.0.0.1:8000/docs`
    2. 點選try it out 即可開始測試
- postman
    1. 下載postman
    2. 選取api的方法（get,post...）
    3. 使用post時，在body的部分輸入測試內容

### [pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines)
- 找到NerPipeline（TokenClassificationPipeline）
- 可以使用pytorch或tensorflow的模型，以下使用pytorch示範
```python
mode = "ckiplab/albert-base-chinese"
tokenizer = "bert-base-chinese"
word = ["馬斯克登富比世全球首富，台灣首富是神秘鞋王張聰淵"]
nlp = pipeline("ner", model=model, tokenizer=tokenizer)
ner_results = nlp(word)
# model (PreTrainedModel or TFPreTrainedModel) 
# aggregation_strategy="simple" # 將同種類進行合併
# ignore_labels=[""] # 預設會忽略"O"
```

### [docker](https://www.docker.com/)
- 為什麼要使用docker?<br>
因為每台電腦的作業系統與硬體配置有可能不同，我的程式碼可能剛好只跟我電腦上的環境相容，因此在其他的電腦使用時可能會爆掉、無法使用。
- 如何使用docker
    1. 安裝 Docker
    2. 準備打包資料和requirements.txt<br>
    將所有需要的套件寫入requirements.txt
    ```
    # 舉例
    fastapi>=0.68.0,<0.69.0
    pydantic>=1.8.0,<2.0.0
    uvicorn>=0.15.0,<0.16.0
    ```
    資料放置方式示範
    ```
    .
    ├── app
    │   ├── __init__.py
    │   └── main.py
    ├── Dockerfile
    └── requirements.txt

    ```
    3. 撰寫 Dockerfile
    ```
    FROM python:3.9
    WORKDIR /code # 在docker裡增加一個叫code的資料夾
    
    # 安裝使用環境
    COPY ./requirements.txt /code/requirements.txt
    RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

    # 複製檔案、資料（複製local的app資料夾到docker的 code/app資料夾）
    COPY ./app /code/app
    
    # run program的方法
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

    ```
    4. Docker build<br>
    `docker build -t name:tag .`<br>
    `docker build -t yihsuan-ner-api:3.9v1 .`
    5. Docker run<br>
    `docker run -d --name mycontainer -p 80:80 myimage`<br>
    `docker run -d --name yihsuan-api -p 80:80 yihsuan-ner-api:3.9v1`

    