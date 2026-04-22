from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.social.router_admin import router as admin_social_router
from app.social.router_internal import router as internal_router

app = FastAPI(title="KDP ULYXEOS Social Admin")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(admin_social_router)
app.include_router(internal_router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "KDP ULYXEOS social module running"}