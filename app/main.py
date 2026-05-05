from fastapi import FastAPI
import os
import sqlite3
import time
import uuid
from fastapi import UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import unquote

# Routers existants
from app.social.router_admin import router as admin_router
from app.social.router_internal import router as internal_router

app = FastAPI()

# --------------------------------------------------
# 📁 STATIC FILES (CSS, JS, etc.)
# --------------------------------------------------

if os.path.isdir("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --------------------------------------------------
# 📁 MEDIA FILES (IMPORTANT POUR INSTAGRAM)
# --------------------------------------------------

IMAGE_DIR = "/var/data/social/images"
VIDEO_DIR = "/var/data/social/videos"
MEDIA_DB = "/var/data/social/media.db"
BASE_URL = "https://kdp-ulyxeos-social.onrender.com"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(MEDIA_DB), exist_ok=True)

# Exposition publique

app.mount("/media/images", StaticFiles(directory=IMAGE_DIR), name="images")
app.mount("/media/videos", StaticFiles(directory=VIDEO_DIR), name="videos")

def init_media_db():
    conn = sqlite3.connect(MEDIA_DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            media_type TEXT NOT NULL,
            public_url TEXT NOT NULL,
            file_path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_media_db()


# --------------------------------------------------
# 🔐 ROUTES ADMIN & INTERNAL
# --------------------------------------------------

app.include_router(admin_router)
app.include_router(internal_router)

# --------------------------------------------------
# 🏠 REDIRECTION ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return RedirectResponse(url="/admin/social")

# xxxxx===============================================-----
# xxxxxx======== 🧪 ROUTE TEST (optionnel) ============-----
# xxxxx===============================================-----

@app.get("/health")
def health():
    return {"status": "ok"}

# xxx=============================================------
# xxxx==============================================------
# xxxxx===============================================-----
# xxxxxx========== /ADMIN/SOCIAL/MEDIA ================-----
# xxxxx===============================================-----
# xxxx==============================================-----
# xxx=============================================-----

from urllib.parse import quote

# @app.get("/admin/social/media", response_class=HTMLResponse)
# def admin_media_page(request: Request):
#     media_items = []
#     item_id = 1
# 
#     for filename in os.listdir(IMAGE_DIR):
#         file_path = os.path.join(IMAGE_DIR, filename)
#         if os.path.isfile(file_path):
#             media_items.append({
#                "id": item_id,
#                 "filename": filename,
#                 "media_type": "image",
#                 "public_url": f"{BASE_URL}/media/images/{quote(filename)}",
#                 "file_path": file_path,
#                 "created_at": time.strftime(
#                     "%Y-%m-%d %H:%M:%S",
#                     time.localtime(os.path.getmtime(file_path))
#                 )
#             })
#             item_id += 1
# 
#     for filename in os.listdir(VIDEO_DIR):
#         file_path = os.path.join(VIDEO_DIR, filename)
#         if os.path.isfile(file_path):
#             media_items.append({
#                 "id": item_id,
#                 "filename": filename,
#                 "media_type": "video",
#                 "public_url": f"{BASE_URL}/media/videos/{quote(filename)}",
#                 "file_path": file_path,
#                 "created_at": time.strftime(
#                     "%Y-%m-%d %H:%M:%S",
#                     time.localtime(os.path.getmtime(file_path))
#                 )
#             })
#             item_id += 1
# 
#     return templates.TemplateResponse(
#         "admin_media.html",
#         {
#             "request": request,
#             "media_items": media_items
#         }
#     )

# =================================================
# ==================================================
# =================================================


@app.get("/admin/social/media")
def admin_social_media():
    return RedirectResponse("/admin/social/media-clean", status_code=302)
      
# =================================================
# ==================================================
# =================================================

# ---------------------------------------------------------
# ================ /admin/social/media/upload =============
# ---------------------------------------------------------

@app.post("/admin/social/media/upload")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    media_type: str = Form(...)
):
    # 🔒 Sécurité admin (si tu l'utilises)
    try:
        if not is_admin_authenticated(request):
            return RedirectResponse("/admin/login", status_code=303)
    except:
        pass  # si tu n’as pas encore la fonction

    # 📁 Dossiers
    IMAGE_DIR = "/var/data/social/images"
    VIDEO_DIR = "/var/data/social/videos"
    MEDIA_DB = "/var/data/social/media.db"
    BASE_URL = "https://kdp-ulyxeos-social.onrender.com"

    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)

    # 📄 Nom fichier original + extension
    original_name = file.filename or "media"
    ext = os.path.splitext(original_name)[1].lower()

    # ⚡ Nom automatique propre
    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:8]

    if media_type == "image":
        filename = f"image_{timestamp}_{unique_id}{ext}"
        folder = IMAGE_DIR
        public_folder = "images"
    elif media_type == "video":
        filename = f"video_{timestamp}_{unique_id}{ext}"
        folder = VIDEO_DIR
        public_folder = "videos"
    else:
        filename = f"media_{timestamp}_{unique_id}{ext}"
        folder = IMAGE_DIR
        public_folder = "images"

    file_path = os.path.join(folder, filename)

    # 💾 Sauvegarde fichier
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # 🌍 URL publique
    public_url = f"{BASE_URL}/media/{public_folder}/{filename}"

    # 🗃️ Sauvegarde DB
    conn = sqlite3.connect(MEDIA_DB)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            media_type TEXT,
            public_url TEXT,
            file_path TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        INSERT INTO media (filename, media_type, public_url, file_path, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (filename, media_type, public_url, file_path))

    conn.commit()
    conn.close()

    # 🔁 Redirection
    return RedirectResponse("/admin/social/media", status_code=303)

# xxx=============================================------
# xxxx==============================================------
# xxxxx===============================================-----
# xxxxxx===== /admin/social/media/delete ==============-----
# xxxxx===============================================-----
# xxxx==============================================-----
# xxx=============================================-----

@app.post("/admin/social/media/delete-clean")
def delete_media_clean(file_path: str = Form("")):
    print("DELETE CLEAN FILE PATH =", file_path)

    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        print("DELETE CLEAN OK")

    return RedirectResponse("/admin/social/media-clean", status_code=303)

# xxx=============================================------
# xxxx==============================================------
# xxxxx===============================================-----
# xxxxxx========== /debug/media-db ====================-----
# xxxxx===============================================-----
# xxxx==============================================-----
# xxx=============================================-----

@app.get("/debug/media-db")
def debug_media_db():
    conn = sqlite3.connect(MEDIA_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, filename, file_path, public_url FROM media ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    return {
        "MEDIA_DB": MEDIA_DB,
        "count": len(rows),
        "items": [dict(row) for row in rows]
    }
# ================================================================
def get_file_path_from_public_url(public_url: str):
    if not public_url:
        return ""

    if "/media/images/" in public_url:
        filename = public_url.split("/media/images/")[-1]
        return os.path.join(IMAGE_DIR, unquote(filename))

    if "/media/videos/" in public_url:
        filename = public_url.split("/media/videos/")[-1]
        return os.path.join(VIDEO_DIR, unquote(filename))

    return ""

# xxx=============================================------
# xxxx==============================================------
# xxxxx===============================================-----
# xxxxxx===== /admin/social/media-clean ===============-----
# xxxxx===============================================-----
# xxxx==============================================-----
# xxx=============================================-----

@app.get("/admin/social/media-clean", response_class=HTMLResponse)
def admin_media_clean():
    html = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Médias Clean</title>
        <style>
            body { font-family:Arial; background:#0f172a; color:white; padding:30px; }
            .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:18px; }
            .card { background:#111827; border:1px solid #334155; border-radius:16px; padding:16px; margin-bottom:20px; }
            img, video { width:100%; max-height:180px; object-fit:cover; border-radius:12px; }
            input, select { width:100%; padding:12px; border-radius:10px; border:1px solid #475569; background:#020617; color:white; margin:8px 0; }
            button { width:100%; margin-top:12px; padding:12px; border:0; border-radius:10px; color:white; font-weight:bold; cursor:pointer; }
            .upload { background:#2563eb; }
            .delete { background:#dc2626; }
            a { color:#fde68a; }
        </style>
    </head>
    <body>
        <h1>Bibliothèque médias — Gestion</h1>
       <div style="margin-bottom:20px;">
    <a href="/admin/social" style="
        display:inline-flex;
        align-items:center;
        gap:10px;
        padding:12px 18px;
        border-radius:12px;
        background:linear-gradient(135deg,#2563eb,#1d4ed8);
        color:white;
        text-decoration:none;
        font-weight:700;
        font-size:14px;
        box-shadow:0 8px 20px rgba(37,99,235,0.3);
        transition:all 0.2s ease;
    "
    onmouseover="this.style.transform='translateY(-2px)'"
    onmouseout="this.style.transform='translateY(0px)'"
    >
        📊 Retour au Dashboard
    </a>
</div>

        <div class="card">
            <h2>Ajouter un média</h2>
            <form method="post" action="/admin/social/media/upload" enctype="multipart/form-data">
                <label>Type</label>
                <select name="media_type" required>
                    <option value="image">Image</option>
                    <option value="video">Vidéo</option>
                </select>

                <label>Fichier</label>
                
<label for="mediaFile" style="
    display:flex;
    align-items:center;
    justify-content:center;
    gap:10px;
    width:100%;
    padding:18px;
    margin-top:10px;
    border-radius:14px;
    border:2px dashed #475569;
    background:#020617;
    color:#cbd5e1;
    font-weight:700;
    cursor:pointer;
">
    📁 Choisir un fichier média
</label>

<input id="mediaFile" type="file" name="file" required style="display:none;">
<div id="selectedFileName" style="
    margin-top:10px;
    color:#94a3b8;
    font-size:13px;
">
    Aucun fichier sélectionné
</div>

<button class="upload" type="submit">
    ✅ Ajouter le média
</button>

<script>
document.getElementById("mediaFile").addEventListener("change", function() {
    const name = this.files.length ? this.files[0].name : "Aucun fichier sélectionné";
    document.getElementById("selectedFileName").innerText = name;
});
</script>

</form>
    </div>

        <h2>Médias enregistrés</h2>
        <div class="grid">
    """

    for filename in os.listdir(IMAGE_DIR):
        file_path = os.path.join(IMAGE_DIR, filename)
        if os.path.isfile(file_path):
            url = "/media/images/" + filename.replace(" ", "%20")
            html += f"""
            <div class="card">
                <img src="{url}">
                <h3>{filename}</h3>
                <form method="post" action="/admin/social/media/delete-clean">
                    <input type="hidden" name="file_path" value="{file_path}">
                    <button class="delete" type="submit" onclick="return confirm('Supprimer ce média ?')">🗑 Supprimer</button>
                </form>
            </div>
            """

    for filename in os.listdir(VIDEO_DIR):
        file_path = os.path.join(VIDEO_DIR, filename)
        if os.path.isfile(file_path):
            url = "/media/videos/" + filename.replace(" ", "%20")
            html += f"""
            <div class="card">
                <video src="{url}" controls></video>
                <h3>{filename}</h3>
                <form method="post" action="/admin/social/media/delete-clean">
                    <input type="hidden" name="file_path" value="{file_path}">
                    <button class="delete" type="submit" onclick="return confirm('Supprimer ce média ?')">🗑 Supprimer</button>
                </form>
            </div>
            """

    html += """
        </div>
    </body>
    </html>
    """

    return html

# xxx=============================================------
# xxxx==============================================------
# xxxxx===============================================-----
# xxxxxx================================================-----
# xxxxx===============================================-----
# xxxx==============================================-----
# xxx=============================================-----


