import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import pytesseract
import cv2
import numpy as np
from io import BytesIO

app = FastAPI()

# --- IMPORTANT: VERIFY THIS PATH ---
# Tell pytesseract where the Tesseract program is installed on your computer.
# The default path for a 64-bit installation on Windows is shown below.
# Double-check this path and correct it if you installed it somewhere else.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# --- MinIO Configuration ---
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "documents"

s3_client = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

class FileInfo(BaseModel):
    filename: str

def preprocess_image(image_stream):
    """Converts image to grayscale and applies thresholding to clean it up."""
    # Read the image from the stream into a format OpenCV can use
    image_array = np.frombuffer(image_stream.read(), np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply a binary threshold to make it black and white
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    return thresh

@app.post("/ocr/")
async def perform_ocr(info: FileInfo):
    try:
        # Download the file from MinIO into memory
        file_obj = BytesIO()
        s3_client.download_fileobj(BUCKET_NAME, info.filename, file_obj)
        file_obj.seek(0)

        # Preprocess the image for better OCR accuracy
        preprocessed_image = preprocess_image(file_obj)

        # Use Tesseract to extract text (English + Malayalam)
        text = pytesseract.image_to_string(preprocessed_image, lang='eng+mal')
        
        # Save the extracted text to a new .txt file in MinIO
        new_filename = os.path.splitext(info.filename)[0] + "_ocr.txt"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=new_filename,
            Body=text.encode('utf-8')
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "OCR successful", "original_file": info.filename, "text_file": new_filename}

@app.get("/")
def root():
    return {"message": "Module C - OCR service is running!"}