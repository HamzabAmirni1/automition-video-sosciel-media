import os
import sys
import json
import shutil
import zipfile
import requests
import asyncio
from fastapi import FastAPI, BackgroundTasks, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.classes.YouTube import YouTube
from src.classes.Twitter import Twitter
from src.classes.TikTok import TikTok
from src.classes.Facebook import Facebook
from src.classes.AFM import AffiliateMarketing
from src.classes.Outreach import Outreach
from src.classes.Tts import TTS
from src.config import *
from src.utils import *
from src.status import *

app = FastAPI(title="MoneyPrinterV2 API", description="Cloud-ready API for MoneyPrinterV2")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global status log
logs = []

def log_info(msg):
    log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(log_entry)
    logs.append(log_entry)
    if len(logs) > 1000:
        logs.pop(0)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Override status functions to capture logs
def success(message):
    log_info(f"✅ SUCCESS: {message}")

def error(message, color="red"):
    log_info(f"❌ ERROR: {message}")

def info(message, show=True):
    if show:
        log_info(f"ℹ️ INFO: {message}")

def warning(message, show=True):
    if show:
        log_info(f"⚠️ WARNING: {message}")

# Mocking status.py functions for our API
import src.status as status_mod
status_mod.success = success
status_mod.error = error
status_mod.info = info
status_mod.warning = warning

@app.on_event("startup")
def startup_event():
    assert_folder_structure()
    rem_temp_files()
    try:
        fetch_songs()
    except:
        log_info("Could not fetch songs on startup, will retry when needed.")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/logs")
def get_logs():
    return {"logs": logs}

@app.get("/config")
def get_config():
    config_path = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {"message": "config.json not found, using environment variables"}

@app.post("/config/update")
async def update_config(data: dict):
    config_path = os.path.join(os.getcwd(), "config.json")
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
    return {"message": "Config updated"}

@app.post("/profile/upload")
async def upload_profile(file: UploadFile = File(...)):
    """Upload a zipped Firefox profile"""
    profile_dir = os.path.join(os.getcwd(), "firefox_profile")
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
    
    os.makedirs(profile_dir)
    zip_path = os.path.join(os.getcwd(), "profile.zip")
    
    with open(zip_path, "wb") as buffer:
        buffer.write(await file.read())
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(profile_dir)
        
    os.remove(zip_path)
    # Update config.json to use this profile
    config = {}
    config_path = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    
    config["firefox_profile"] = os.path.abspath(profile_dir)
    config["headless"] = True
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        
    return {"message": "Profile uploaded and configured", "path": config["firefox_profile"]}

# Background Task Runners

async def run_youtube_automation(niche, language, nickname, profile_path):
    try:
        log_info(f"Starting YouTube automation for {nickname} ({niche})...")
        yt = YouTube(str(uuid4()), nickname, profile_path, niche, language)
        tts = TTS()
        log_info("Generating video...")
        path = yt.generate_video(tts)
        log_info(f"Video generated at {path}. Uploading...")
        yt.upload_video()
        log_info("YouTube automation completed successfully!")
    except Exception as e:
        log_info(f"YouTube automation failed: {str(e)}")

@app.post("/youtube/generate")
async def generate_youtube(
    background_tasks: BackgroundTasks, 
    niche: str = Form("Motivation"), 
    language: str = Form("English"),
    nickname: str = Form("MyChannel")
):
    profile_path = get_firefox_profile_path()
    if not profile_path or not os.path.exists(profile_path):
        return JSONResponse(status_code=400, content={"message": "Firefox profile not found. Please upload one first."})
    
    background_tasks.add_task(run_youtube_automation, niche, language, nickname, profile_path)
    return {"message": "YouTube automation started in background"}

async def run_twitter_post(nickname, profile_path, topic):
    try:
        log_info(f"Starting Twitter post for {nickname}...")
        tw = Twitter(str(uuid4()), nickname, profile_path, topic)
        tw.post()
        log_info("Twitter post completed successfully!")
    except Exception as e:
        log_info(f"Twitter post failed: {str(e)}")

@app.post("/twitter/post")
async def post_twitter(
    background_tasks: BackgroundTasks,
    nickname: str = Form("MyTwitter"),
    topic: str = Form("AI and Technology")
):
    profile_path = get_firefox_profile_path()
    if not profile_path or not os.path.exists(profile_path):
        return JSONResponse(status_code=400, content={"message": "Firefox profile not found. Please upload one first."})
    
    background_tasks.add_task(run_twitter_post, nickname, profile_path, topic)
    return {"message": "Twitter post started in background"}

async def run_omni_automation(niche, language, nickname, profile_path, platforms: List[str]):
    try:
        log_info(f"🚀 Starting Omni-Automation for {nickname} on {', '.join(platforms)}...")
        
        # 1. Generate Video once
        yt = YouTube(str(uuid4()), nickname, profile_path, niche, language)
        tts = TTS()
        log_info("🎬 Generating shared video content...")
        video_path = yt.generate_video(tts)
        metadata = yt.metadata
        log_info(f"✅ Video generated at {video_path}")

        # 2. Upload to selected platforms
        if "youtube" in platforms:
            try:
                log_info("📺 Uploading to YouTube...")
                yt.upload_video()
            except Exception as e: log_info(f"❌ YouTube upload failed: {e}")

        if "tiktok" in platforms:
            try:
                log_info("🎵 Uploading to TikTok...")
                tk = TikTok(str(uuid4()), nickname, profile_path, niche)
                tk.upload_video(video_path, metadata["title"])
            except Exception as e: log_info(f"❌ TikTok upload failed: {e}")

        if "facebook" in platforms:
            try:
                log_info("👥 Uploading to Facebook Reels...")
                fb = Facebook(str(uuid4()), nickname, profile_path, niche)
                fb.upload_reel(video_path, metadata["title"])
            except Exception as e: log_info(f"❌ Facebook upload failed: {e}")

        log_info("🏁 Omni-Automation task finished.")
    except Exception as e:
        log_info(f"🚨 Omni-Automation failed: {str(e)}")

@app.post("/omni/generate")
async def generate_omni(
    background_tasks: BackgroundTasks,
    niche: str = Form("Motivation"),
    language: str = Form("English"),
    nickname: str = Form("MyBrand"),
    platforms: str = Form("youtube,tiktok,facebook") # Comma separated
):
    profile_path = get_firefox_profile_path()
    if not profile_path or not os.path.exists(profile_path):
        return JSONResponse(status_code=400, content={"message": "Firefox profile not found. Please upload one first."})
    
    selected_platforms = [p.strip() for p in platforms.split(",") if p.strip()]
    background_tasks.add_task(run_omni_automation, niche, language, nickname, profile_path, selected_platforms)
    return {"message": f"Omni-Automation started for: {', '.join(selected_platforms)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
