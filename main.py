import os
import json
from typing import Dict
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path


class FileItem(BaseModel):
    filename: str


class ChatGPT:
    def __init__(self):
        self.dataset = []

    def add_data_from_file(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                self.dataset.append(line.strip())

    def generate_response(self, query: str) -> str:
        # Your code to generate a response here
        return "This is a response from ChatGPT."

    def get_dataset(self) -> Dict[str, str]:
        return {"dataset": self.dataset}


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt'}
app = FastAPI()
chatbot = ChatGPT()


def load_manifest():
    with open("manifest.json", "r") as f:
        return json.load(f)


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def ai_plugin():
    manifest = load_manifest()
    return JSONResponse(content=manifest)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if allowed_file(file.filename):
        file_name = Path(file.filename).stem
        file_ext = Path(file.filename).suffix
        save_path = f"{file_name}_{str(hash(file))}{file_ext}"
        with open(save_path, "wb") as f:
            f.write(await file.read())
        chatbot.add_data_from_file(save_path)
        os.remove(save_path)
        return {"filename": file.filename}
    else:
        raise HTTPException(status_code=400, detail="Invalid file type.")


@app.get("/dataset/")
async def get_dataset():
    return chatbot.get_dataset()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ChatGPT",
        version="1.0.0",
        description="A chatbot app using ChatGPT and FastAPI",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")
