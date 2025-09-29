from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from typing import Annotated
import requests
import boto3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "documents"

s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=boto3.session.Config(signature_version='s3v4')
)

@app.post("/upload/")
async def create_upload_file(source: Annotated[str, Form()] = "ManualUpload", file: UploadFile = File(...)):
    temp_storage_path = f"temp/{file.filename}"
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, temp_storage_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file to MinIO: {e}")

    try:
        requests.post("http://module-b:8000/process/", json={"filename": file.filename, "source": source})
    except requests.exceptions.RequestException as e:
        print(f"CRITICAL ERROR: Could not trigger Module B. Is it running? Error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing service is unavailable: {e}")

    return {"message": "File received and processing started."}


