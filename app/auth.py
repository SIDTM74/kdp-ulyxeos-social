from fastapi import Request, Form
from fastapi.responses import RedirectResponse
from itsdangerous import URLSafeSerializer, BadSignature
from app.config import SESSION_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD

serializer = URLSafeSerializer(SESSION_SECRET, salt="admin-session")


def create_session_token(email: str) -> str:
    return serializer.dumps({"email": email, "is_admin": True})


def read_session_token(token: str):
    try:
        return serializer.loads(token)
    except BadSignature:
        return None


def is_admin_authenticated(request: Request) -> bool:
    token = request.cookies.get("admin_session")
    if not token:
        return False

    data = read_session_token(token)
    return bool(data and data.get("is_admin") is True)


def login_is_valid(email: str, password: str) -> bool:
    return email == ADMIN_EMAIL and password == ADMIN_PASSWORD


def admin_required(request: Request) -> None:
    if not is_admin_authenticated(request):
        raise PermissionError("Admin authentication required")