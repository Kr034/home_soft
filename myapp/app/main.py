# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from converter import convert_md_to_pdf
from pathlib import Path
import os
import yaml
import requests
import json
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "/data/uploads"
OUTPUT_DIR = "/data/outputs"
LOG_DIR = "/data/logs"
PASTE_DIR = "/data/pasted"
SCRIPTS_DIR = "/data/scripts"
HISTORY_DIR = "/data/history"

for d in [UPLOAD_DIR, OUTPUT_DIR, LOG_DIR, PASTE_DIR, SCRIPTS_DIR, HISTORY_DIR]:
    os.makedirs(d, exist_ok=True)

def load_categories(path="categories.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@app.get("/")
async def dashboard(request: Request):
    uploads = sorted([f.name for f in Path(UPLOAD_DIR).glob("*.md")])
    outputs = sorted([f.name for f in Path(OUTPUT_DIR).glob("*.pdf")])
    logs = []
    log_path = Path(LOG_DIR) / "conversions.log"
    if log_path.exists():
        logs = log_path.read_text().splitlines()[-10:]
    categories = load_categories()
    scripts = []
    for fname in os.listdir(SCRIPTS_DIR):
        path = os.path.join(SCRIPTS_DIR, fname)
        desc = ""
        try:
            with open(path) as f:
                for line in f:
                    if line.strip().startswith("#"):
                        desc = line.strip().lstrip("#").strip()
                        break
        except Exception:
            desc = ""
        scripts.append({"name": fname, "desc": desc})

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "uploads": uploads,
        "outputs": outputs,
        "logs": logs,
        "categories": categories,
        "scripts": scripts
    })

@app.get("/edit")
async def edit_script_page(request: Request, name: str):
    path = os.path.join(SCRIPTS_DIR, name)
    content = ""
    if os.path.exists(path):
        content = Path(path).read_text()
    return templates.TemplateResponse("sections/edit_script.html", {
        "request": request,
        "script_name": name,
        "script_content": content
    })

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return RedirectResponse(url="/", status_code=303)

@app.post("/paste")
async def paste_content(name: str = Form(...), content: str = Form(...)):
    md_filename = name if name.endswith(".md") else name + ".md"
    input_path = os.path.join(PASTE_DIR, md_filename)
    output_path = os.path.join(OUTPUT_DIR, md_filename.replace(".md", ".pdf"))
    with open(input_path, "w") as f:
        f.write(content)
    convert_md_to_pdf(input_path, output_path)
    return RedirectResponse(url="/", status_code=303)

@app.post("/convert-file")
async def convert_file(filename: str = Form(...)):
    input_path = os.path.join(UPLOAD_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename.replace(".md", ".pdf"))
    convert_md_to_pdf(input_path, output_path)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete")
async def delete_file(filename: str = Form(...), filetype: str = Form(...)):
    dir_map = {"upload": UPLOAD_DIR, "output": OUTPUT_DIR, "pasted": PASTE_DIR}
    path = os.path.join(dir_map[filetype], filename)
    if os.path.exists(path):
        os.remove(path)
    return RedirectResponse(url="/", status_code=303)

@app.post("/add-script")
async def add_script(script_name: str = Form(...), script_content: str = Form(...)):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-script")
async def delete_script(script_name: str = Form(...)):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if os.path.exists(script_path):
        os.remove(script_path)
    return RedirectResponse(url="/", status_code=303)

@app.post("/edit-script")
async def edit_script(script_name: str = Form(...), script_content: str = Form(...)):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)
    return RedirectResponse(url="/", status_code=303)

@app.post("/run-script")
async def run_script(script_name: str = Form(...)):
    path = os.path.join(SCRIPTS_DIR, script_name)
    if os.path.exists(path):
        os.system(f"bash {path}")
    return RedirectResponse(url="/", status_code=303)


@app.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    history_path = "/data/history/conversations.json"
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(history_path) or os.path.getsize(history_path) == 0:
        with open(history_path, "w") as f:
            json.dump([], f)

    # Chargement sécurisé
    try:
        with open(history_path, "r") as f:
            conversations = json.load(f)
    except json.JSONDecodeError:
        conversations = []

    return templates.TemplateResponse("sections/history.html", {
        "request": request,
        "conversations": conversations
    })

@app.post("/ask-ai")
async def ask_ai(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    history_path = "/data/history/conversations.json"

    try:
        r = requests.post("http://localhost:11434/api/generate", json={
            "model": "codellama:7b-instruct",
            "prompt": prompt,
            "stream": False
        })
        result = r.json()
        response = result.get("response", "Pas de réponse.")

        # Enregistrer la discussion
        entry = {
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.datetime.now().isoformat()
        }


        if not os.path.exists(history_path) or os.path.getsize(history_path) == 0:
            with open(history_path, "w") as f:
                json.dump([], f)

        # Chargement sécurisé
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

        history.append(entry)

        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"response": f"Erreur : {e}"}, status_code=500)

@app.get("/scripts-list")
async def list_scripts():
    scripts = []
    for fname in os.listdir(SCRIPTS_DIR):
        path = os.path.join(SCRIPTS_DIR, fname)
        desc = ""
        try:
            with open(path) as f:
                for line in f:
                    if line.strip().startswith("#"):
                        desc = line.strip().lstrip("#").strip()
                        break
        except Exception:
            desc = ""
        scripts.append({"name": fname, "desc": desc})
    return scripts

app.mount("/static", StaticFiles(directory="/data"), name="static")