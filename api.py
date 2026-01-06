import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from chat import ask_hr_bot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(title="HR Policy RAG Chatbot")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)



@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "answer": None}
    )


@app.post("/chat", response_class=HTMLResponse)
def chat(request: Request, question: str = Form(...)):
    result = ask_hr_bot(question)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "question": question,
            "answer": result["answer"],
            "mode": result["mode"],
            "sources": result["sources"]
        }
    )

