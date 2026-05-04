from fastapi import FastAPI
import os
import sqlite3
import time
from fastapi import UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

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

# ---------------------------------------------------------
# ================ /admin/social/media ====================
# ---------------------------------------------------------
@app.get("/admin/social/media", response_class=HTMLResponse)
def admin_media_page():
    conn = sqlite3.connect(MEDIA_DB)
    c = conn.cursor()

    c.execute("""
        SELECT id, filename, media_type, public_url, file_path, created_at
        FROM media
        ORDER BY id DESC
    """)

    medias = c.fetchall()
    conn.close()

    rows = ""

    for media_id, filename, media_type, public_url, file_path, created_at in medias:
        if media_type == "image":
            preview = f"""
            <img src="{public_url}" style="width:100%;max-height:180px;object-fit:cover;border-radius:12px;">
            """
        else:
            preview = f"""
            <video src="{public_url}" controls style="width:100%;max-height:180px;border-radius:12px;"></video>
            """

        rows += f"""
        <div class="media-card">
            {preview}

            <h3>{filename}</h3>
            <p><strong>Type :</strong> {media_type}</p>
            <p><strong>Date :</strong> {created_at}</p>

            <p>
                <a href="{public_url}" target="_blank">Voir le média</a>
            </p>

            <form method="post" action="/admin/social/media/delete">
                <input type="hidden" name="media_id" value="{media_id}">
                <button type="submit" class="delete-btn"
                        onclick="return confirm('Supprimer définitivement ce média ?')">
                    🗑 Supprimer
                </button>
            </form>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <title>Médias - KDP ULYXEOS Social</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background:#0f172a;
                color:white;
                padding:30px;
                margin:0;
            }}

            .nav {{
                margin-bottom:25px;
            }}

            .nav a {{
                color:#fde68a;
                margin-right:15px;
                text-decoration:none;
                font-weight:bold;
            }}

            .card {{
                background:#111827;
                padding:22px;
                border-radius:18px;
                margin-bottom:25px;
                border:1px solid #334155;
            }}

            input, select {{
                padding:12px;
                border-radius:10px;
                border:1px solid #475569;
                background:#020617;
                color:white;
                margin:8px 0;
            }}

            button {{
                padding:12px 18px;
                border:none;
                border-radius:12px;
                background:#2563eb;
                color:white;
                font-weight:bold;
                cursor:pointer;
            }}

            .delete-btn {{
                width:100%;
                margin-top:12px;
                background:#dc2626;
                color:white;
            }}

            .grid {{
                display:grid;
                grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
                gap:18px;
            }}

            .media-card {{
                background:#111827;
                padding:18px;
                border-radius:18px;
                border:1px solid #334155;
            }}

            .media-card h3 {{
                font-size:15px;
                word-break:break-all;
            }}

            a {{
                color:#93c5fd;
            }}
        </style>
    </head>

    <body>

        <div class="nav">
            <a href="/admin/social">Dashboard</a>
            <a href="/admin/social/media">Médias</a>
            <a href="/admin/social/history">Historique</a>
        </div>

        <h1>Bibliothèque médias</h1>
        <h2 style="color:red;">TEST BOUTON SUPPRESSION VERSION 2</h2>
        
        <div class="card">
            <h2>Ajouter un média</h2>

            <form method="post" action="/admin/social/media/upload" enctype="multipart/form-data">
                <div>
                    <label>Type :</label><br>
                    <select name="media_type" required>
                        <option value="image">Image</option>
                        <option value="video">Vidéo</option>
                    </select>
                </div>

                <div>
                    <input type="file" name="file" required>
                </div>

                <button type="submit">Ajouter le média</button>
            </form>
        </div>

        <h2>Médias enregistrés</h2>
        
        <div class="grid">
            {rows if rows else "<p>Aucun média enregistré.</p>"}
        </div>

    </body>
    </html>
    """
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
@app.post("/admin/social/media/delete")
def delete_media(request: Request, media_id: int = Form(...)):
    if not is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)

    conn = sqlite3.connect(MEDIA_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM media WHERE id = ?", (media_id,))
    media = cur.fetchone()

    if not media:
        conn.close()
        return RedirectResponse("/admin/social/media", status_code=303)

    file_path = media["file_path"] if "file_path" in media.keys() else None

    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    cur.execute("DELETE FROM media WHERE id = ?", (media_id,))
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/social/media", status_code=303)
    


# -------------------------------------------------

# -------------------------------------------------


