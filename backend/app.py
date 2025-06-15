from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from typing import Optional  # Added for better type hints

# Import your speaker comparison function
from .resembletest import compare_speakers

# Ensure upload directory exists
UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/verify", response_class=HTMLResponse)
async def verify(
    request: Request, 
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...)
):
    try:
        # Validate file types
        if not (file1.filename.endswith('.wav') and file2.filename.endswith('.wav')):
            return templates.TemplateResponse("frontend/index.html", {
                "request": request,
                "error": "Please upload .wav files only"
            })
        
        # Create unique filenames to avoid conflicts
        path1 = os.path.join(UPLOAD_DIR, f"file1_{file1.filename}")
        path2 = os.path.join(UPLOAD_DIR, f"file2_{file2.filename}")

        # Save files
        with open(path1, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        
        with open(path2, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)

        # Verify files were saved
        if not (os.path.exists(path1) and os.path.exists(path2)):
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Failed to save uploaded files"
            })

        # Compare speakers
        result = compare_speakers(path1, path2)
        
        # Clean up uploaded files after processing
        try:
            os.remove(path1)
            os.remove(path2)
        except Exception as e:
            print(f"Error cleaning up files: {e}")

        return templates.TemplateResponse("index.html", {
            "request": request,
            "similarity": result.get("similarity", "N/A"),
            "same_speaker": result.get("same_speaker", False),
            "success": True
        })

    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"An error occurred: {str(e)}"
        })