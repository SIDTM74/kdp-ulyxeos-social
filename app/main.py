from fastapi import FastAPI
import os
import sqlite3
import time
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
app.mount("/media/images", StaticFiles(directory=IMAGE_DIR), name="media_images")
app.mount("/media/videos", StaticFiles(directory=VIDEO_DIR), name="media_videos")

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

# --------------------------------------------------
# 🧪 ROUTE TEST (optionnel)
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}
# ======================================================
# =======================================================
# ========= / A D M I N / S O C I A L / M E D I A =========
# =======================================================
# ======================================================
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
  def admin_social_media_redirect():
    return RedirectResponse("/admin/social/media-clean", status_code=303)
      
# =================================================
# ==================================================
# =================================================

# ---------------------------------------------------------
# ================ /admin/social/media/upload =============
# ---------------------------------------------------------

@app.post("/admin/social/media/upload")
async def upload_media(
    media_type: str = Form(...),
    file: UploadFile = File(...)
):
    original_name = file.filename or "media"
    ext = os.path.splitext(original_name)[1].lower()

    if media_type == "image":
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            return HTMLResponse("Format image non autorisé", status_code=400)

        folder = IMAGE_DIR
        public_folder = "images"

    elif media_type == "video":
        if ext not in [".mp4", ".mov", ".webm"]:
            return HTMLResponse("Format vidéo non autorisé", status_code=400)

        folder = VIDEO_DIR
        public_folder = "videos"

    else:
        return HTMLResponse("Type média invalide", status_code=400)

    safe_name = original_name.replace(" ", "_").replace("'", "_").replace('"', "_")
    filename = f"{int(time.time())}_{safe_name}"
    file_path = os.path.join(folder, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    public_url = f"{BASE_URL}/media/{public_folder}/{filename}"

    conn = sqlite3.connect(MEDIA_DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO media (filename, media_type, public_url, file_path, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        media_type,
        public_url,
        file_path,
        time.strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return RedirectResponse("/admin/social/media", status_code=303)
# ------------------------------------------------------------------------
# ================= /admin/social/media/delete ===========================
# ------------------------------------------------------------------------
@app.post("/admin/social/media/delete-clean")
def delete_media_clean(file_path: str = Form("")):
    print("DELETE CLEAN FILE PATH =", file_path)

    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        print("DELETE CLEAN OK")

    return RedirectResponse("/admin/social/media-clean", status_code=303)
# -------------------------------------------------
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
# -------------------------------------------------
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
# -------------------------------------------------
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
            .card { background:#111827; border:1px solid #334155; border-radius:16px; padding:16px; }
            img, video { width:100%; max-height:180px; object-fit:cover; border-radius:12px; }
            button { width:100%; margin-top:12px; padding:12px; border:0; border-radius:10px; background:#dc2626; color:white; font-weight:bold; cursor:pointer; }
            a { color:#fde68a; }
        </style>
    </head>
    <body>
        <h1>Bibliothèque médias — Clean</h1>
        <p><a href="/admin/social">← Retour dashboard</a></p>
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
        <Input type="hidden" name="file_path" value="{file_path}">
            <button type="submit" onclick="return confirm('Supprimer ce média ?')">🗑 Supprimer</button>
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
                    <button type="submit" onclick="return confirm('Supprimer ce média ?')">🗑 Supprimer</button>
                </form>
            </div>
            """

    html += """
        </div>
    </body>
    </html>
    """

    return html




