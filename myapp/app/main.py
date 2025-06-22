# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from converter import convert_md_to_pdf
from pathlib import Path
import uuid, json, os
import yaml
import requests
import datetime
import markdown2

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "/data/uploads"
OUTPUT_DIR = "/data/outputs"
LOG_DIR = "/data/logs"
PASTE_DIR = "/data/pasted"
SCRIPTS_DIR = "/data/scripts"
HISTORY_DIR = "/data/history"

DATA_DIR = Path("data")
HISTORY_FILE = DATA_DIR / "history" / "conversations.json"
for d in [UPLOAD_DIR, OUTPUT_DIR, LOG_DIR, PASTE_DIR, SCRIPTS_DIR, HISTORY_DIR]:
    os.makedirs(d, exist_ok=True)

def load_categories(path="categories.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_conversations():
    items = []
    for fname in sorted(os.listdir(HISTORY_DIR), reverse=True):
        with open(os.path.join(HISTORY_DIR, fname)) as f:
            content = json.load(f)
            items.append({"id": fname[:-5], "created_at": content.get("created_at")})
    return items

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    uploads = sorted([f.name for f in Path(UPLOAD_DIR).glob("*.md")])
    outputs = sorted([f.name for f in Path(OUTPUT_DIR).glob("*.pdf")])
    logs = []
    log_path = Path(LOG_DIR) / "conversions.log"
    if log_path.exists():
        logs = log_path.read_text().splitlines()[-10:]

    categories = load_categories()

    # Chargement des scripts
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

    # 🔍 Correction : chargement de toutes les conversations JSON
    history = []
    for file in Path("/data/history").glob("*.json"):
        try:
            with open(file) as f:
                content = json.load(f)
                created_at = content.get("created_at")
                if not created_at:
                    # fallback : date du fichier si non incluse dans le JSON
                    ts = file.stat().st_mtime
                    created_at = datetime.fromtimestamp(ts).isoformat()
                history.append({
                    "id": file.stem,
                    "created_at": created_at
                })
        except Exception as e:
            print(f"[ERREUR] Lecture {file}: {e}")

    print(f"[INFO] Chargé {len(history)} conversations.")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "uploads": uploads,
        "outputs": outputs,
        "logs": logs,
        "categories": categories,
        "scripts": scripts,
        "ai_history": history  # 👈 utilisé dans le template
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

@app.post("/new-chat", response_class=JSONResponse)
async def new_chat():
    conv_id = str(uuid.uuid4())
    file_path = Path(HISTORY_DIR) / f"{conv_id}.json"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps({
        "id": conv_id,
        "created_at": str(uuid.uuid1().time),  # ou utilise datetime.now().isoformat()
        "messages": []
    }))
    return {"id": conv_id}

@app.get("/data/history/{chat_id}.json")
async def get_chat_json(chat_id: str):
    path = os.path.join(HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        return FileResponse(path, media_type="application/json")
    return JSONResponse({"error": "Not found"}, status_code=404)

@app.post("/ask-ai-chat", response_class=JSONResponse)
async def ask_ai_chat(request: Request):
    data = await request.json()
    conv_id = data["conv_id"]
    prompt = data["prompt"]

    path = os.path.join(HISTORY_DIR, f"{conv_id}.json")

    # 1. Charger les anciens messages
    if os.path.exists(path):
        with open(path) as f:
            content = json.load(f)
    else:
        content = {"messages": []}

    # 2. Ajouter le message utilisateur
    content["messages"].append({
        "role": "user",
        "text": prompt
    })

    # 3. Convertir les messages pour Ollama
    ollama_messages = [{"role": "system", "content": "Tu es un assistant utile, parlant français. L'utilisateur s'appelle Corentin."}]
    for m in content["messages"]:
        ollama_messages.append({
            "role": m["role"],
            "content": m["text"]
        })

    # 4. Appeler Ollama avec le contexte
    try:
        r = requests.post("http://localhost:11434/api/chat", json={
            "model": "deepseek-r1:32b",
            "messages": ollama_messages,
            "stream": False
        })
        result = r.json()
        response_text = result.get("message", {}).get("content", "❌ Aucune réponse.")
    except Exception as e:
        response_text = f"Erreur lors de l'appel au modèle : {e}"

    # 5. Ajouter la réponse de l'IA
    content["messages"].append({
        "role": "assistant",
        "text": response_text
    })

    # 6. Sauvegarder la conversation mise à jour
    with open(path, "w") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    # 7. Convertir la réponse en HTML (Markdown si tu veux)
    html = markdown2.markdown(response_text)

    return {"response": html}


@app.post("/delete-chat")
async def delete_chat(request: Request):
    form = await request.form()
    conv_id = form["conv_id"]
    path = Path(f"/data/history/{conv_id}.json")
    if path.exists():
        path.unlink()
    return RedirectResponse("/", status_code=303)


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
