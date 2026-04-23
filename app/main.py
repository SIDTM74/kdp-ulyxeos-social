import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import SOCIAL_IMAGE_DIR, SOCIAL_VIDEO_DIR
import os
from app.db import init_db
from app.social.router_admin import router as admin_social_router
from app.social.router_internal import router as internal_router

app = FastAPI(title="KDP ULYXEOS Social Admin")

if os.path.isdir("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

if os.path.isdir(SOCIAL_IMAGE_DIR):
    app.mount("/media/images", StaticFiles(directory=SOCIAL_IMAGE_DIR), name="media_images")

if os.path.isdir(SOCIAL_VIDEO_DIR):
    app.mount("/media/videos", StaticFiles(directory=SOCIAL_VIDEO_DIR), name="media_videos")


app.include_router(admin_social_router)
app.include_router(internal_router)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "KDP ULYXEOS social module running"}
