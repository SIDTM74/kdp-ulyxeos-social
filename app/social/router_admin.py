from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

import uuid
import time
import os

from app.auth import (
    login_is_valid, create_session_token,
    is_admin_authenticated
)
from app.db import get_db
from app.social_storage import (
    save_uploaded_media,
    create_media_record,
    update_media_public_url,
)
from app.social.router_internal import run_autopost

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["admin-social"])


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "admin_login.html",
        {}
    )
# //////////////////////////////////////////////////////////////////////////////////////
@router.get("/admin/creator", response_class=HTMLResponse)
def admin_creator_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    return templates.TemplateResponse(
        request,
        "admin_creator.html",
        {}
    )
# //////////////////////////////////////////////////////////////////////////////////////

@router.post("/admin/login")
def admin_login(request: Request, email: str = Form(...), password: str = Form(...)):
    if not login_is_valid(email, password):
        return RedirectResponse("/admin/login", status_code=303)

    response = RedirectResponse("/admin/social", status_code=303)
    response.set_cookie(
        "admin_session",
        create_session_token(email),
        httponly=True,
        samesite="lax"
    )
    return response


@router.get("/admin/social", response_class=HTMLResponse)
def admin_social_dashboard(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM social_settings WHERE id = 1")
    settings = cur.fetchone()

    cur.execute("SELECT * FROM social_posts ORDER BY id DESC LIMIT 10")
    posts = cur.fetchall()

    cur.execute("SELECT * FROM social_runs ORDER BY id DESC LIMIT 5")
    runs = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS total_posts FROM social_posts")
    total_posts = cur.fetchone()["total_posts"]

    cur.execute("SELECT COUNT(*) AS total_runs FROM social_runs")
    total_runs = cur.fetchone()["total_runs"]

    cur.execute("SELECT COUNT(*) AS success_runs FROM social_runs WHERE status = 'success'")
    success_runs = cur.fetchone()["success_runs"]

    cur.execute("SELECT COUNT(*) AS failed_runs FROM social_runs WHERE status = 'failed'")
    failed_runs = cur.fetchone()["failed_runs"]

    cur.execute("SELECT COUNT(*) AS partial_runs FROM social_runs WHERE status = 'partial'")
    partial_runs = cur.fetchone()["partial_runs"]

    cur.execute("SELECT * FROM social_posts ORDER BY id DESC LIMIT 1")
    latest_post = cur.fetchone()

    cur.execute("SELECT * FROM social_runs ORDER BY id DESC LIMIT 1")
    latest_run = cur.fetchone()

    conn.close()

    stats = {
        "total_posts": total_posts,
        "total_runs": total_runs,
        "success_runs": success_runs,
        "failed_runs": failed_runs,
        "partial_runs": partial_runs,
    }

    return templates.TemplateResponse(
        request,
        "admin_social.html",
        {
            "settings": settings,
            "posts": posts,
            "runs": runs,
            "stats": stats,
            "latest_post": latest_post,
            "latest_run": latest_run,
        }
    )


@router.post("/admin/social/post-now")
def admin_post_now(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    try:
        run_autopost(request)
    except Exception as exc:
        print(f"Manual post error: {exc}")

    return RedirectResponse("/admin/social", status_code=303)


@router.post("/admin/social/content-mode")
def update_content_mode(request: Request, content_mode: str = Form(...)):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    if content_mode not in ["standard", "viral", "ultra_aggressive"]:
        return RedirectResponse("/admin/social", status_code=303)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE social_settings
        SET content_mode = ?, updated_at = datetime('now')
        WHERE id = 1
    """, (content_mode,))
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/social", status_code=303)


@router.post("/admin/social/settings")
def update_social_settings(
    request: Request,
    posts_per_day: int = Form(...),
    facebook_enabled: str | None = Form(default=None),
    instagram_enabled: str | None = Form(default=None),
    tiktok_enabled: str | None = Form(default=None),
    bonus_message_enabled: str | None = Form(default=None),
    email_notifications_enabled: str | None = Form(default=None),
):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    posts_per_day = max(1, min(posts_per_day, 12))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE social_settings
        SET posts_per_day = ?,
            facebook_enabled = ?,
            instagram_enabled = ?,
            tiktok_enabled = ?,
            bonus_message_enabled = ?,
            email_notifications_enabled = ?,
            updated_at = datetime('now')
        WHERE id = 1
    """, (
        posts_per_day,
        1 if facebook_enabled == "1" else 0,
        1 if instagram_enabled == "1" else 0,
        1 if tiktok_enabled == "1" else 0,
        1 if bonus_message_enabled == "1" else 0,
        1 if email_notifications_enabled == "1" else 0,
    ))
    conn.commit()
    conn.close()

    return RedirectResponse("/admin/social", status_code=303)

# ===============================================================================
# ===============================================================================
# ===============================================================================

@router.get("/admin/social/media", response_class=HTMLResponse)
def admin_media_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    return RedirectResponse("/admin/social/media-clean", status_code=302)
    
# ===============================================================================
# ===============================================================================
# ===================     /admin/social/media/upload     ========================
# ===============================================================================
# ===============================================================================

from fastapi import UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse
import os
import time
import uuid
import sqlite3

# ⚠️ adapte si tes constantes sont ailleurs
IMAGE_DIR = "/var/data/social/images"
VIDEO_DIR = "/var/data/social/videos"
MEDIA_DB = "/var/data/social/media.db"
BASE_URL = "https://kdp-ulyxeos-social.onrender.com"


@router.post("/admin/social/media/upload")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    media_type: str = Form(...)
):
    # 🔒 Vérification admin (si fonction existe)
    try:
        if not is_admin_authenticated(request):
            return RedirectResponse("/admin/login", status_code=303)
    except:
        pass

    # 📁 Création dossiers si absents
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(VIDEO_DIR, exist_ok=True)

    # 📄 Nom original + extension
    original_name = file.filename or "media"
    ext = os.path.splitext(original_name)[1].lower()

    # ⚡ NOM AUTOMATIQUE (IMPORTANT)
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

    # 📍 Chemin final
    file_path = os.path.join(folder, filename)

    # 💾 Sauvegarde fichier
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 🌍 URL publique
    public_url = f"{BASE_URL}/media/{public_folder}/{filename}"

    # 🗃️ Enregistrement DB
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
# ===============================================================================
# ===============================================================================
# ================   /admin/social/media/public-url   ===========================
# ===============================================================================
# ===============================================================================

@router.post("/admin/social/media/public-url")
def save_media_public_url(
    request: Request,
    media_id: int = Form(...),
    public_url: str = Form(...),
):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    update_media_public_url(media_id, public_url)
    return RedirectResponse("/admin/social/media", status_code=303)


@router.get("/admin/social/history", response_class=HTMLResponse)
def admin_history_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT sp.id, sp.content_text, sp.created_at, sp.status
        FROM social_posts sp
        ORDER BY sp.id DESC
        LIMIT 50
    """)
    posts = cur.fetchall()

    history_rows = []
    for post in posts:
        cur.execute("""
            SELECT platform, status, response_json, sent_at
            FROM social_post_targets
            WHERE social_post_id = ?
            ORDER BY id DESC
        """, (post["id"],))
        targets = cur.fetchall()

        history_rows.append({
            "post": post,
            "targets": targets
        })

    conn.close()

    return templates.TemplateResponse(
        request,
        "admin_history.html",
        {
            "history_rows": history_rows
        }
    )
