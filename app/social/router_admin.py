from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import (
    login_is_valid, create_session_token,
    is_admin_authenticated
)
from app.db import get_db
from app.social_storage import save_uploaded_media, create_media_record
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

    conn.close()

    return templates.TemplateResponse(
        request,
        "admin_social.html",
        {
            "settings": settings,
            "posts": posts,
            "runs": runs
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


@router.get("/admin/social/media", response_class=HTMLResponse)
def admin_media_page(request: Request):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM social_media ORDER BY id DESC")
    media_items = cur.fetchall()
    conn.close()

    return templates.TemplateResponse(
        request,
        "admin_media.html",
        {
            "media_items": media_items
        }
    )


@router.post("/admin/social/media/upload")
def upload_media(
    request: Request,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    platform_hint: str = Form("all")
):
    if not is_admin_authenticated(request):
        return RedirectResponse("/admin/login", status_code=303)

    filepath = save_uploaded_media(file, media_type=media_type)
    create_media_record(
        filename=file.filename,
        filepath=filepath,
        media_type=media_type,
        platform_hint=platform_hint
    )

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
    rows = cur.fetchall()
    conn.close()

    return templates.TemplateResponse(
        request,
        "admin_history.html",
        {
            "rows": rows
        }
    )
