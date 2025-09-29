import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import docx
import pypdf
from io import BytesIO
import requests
import psycopg2
import pandas as pd

app = FastAPI()

# --- Configurations ---
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "documents"
s3_client = boto3.client("s3", endpoint_url=f"http://{MINIO_ENDPOINT}", aws_access_key_id=MINIO_ACCESS_KEY, aws_secret_access_key=MINIO_SECRET_KEY, config=boto3.session.Config(signature_version='s3v4'))
DB_HOST = "postgres"
DB_NAME = "kmrl_docs"
DB_USER = "admin"
DB_PASS = "admin"

class ProcessInfo(BaseModel):
    filename: str
    source: str

def extract_text_from_docx(stream):
    return "\n".join([p.text for p in docx.Document(stream).paragraphs])

def extract_text_from_pdf(stream):
    return "\n".join([p.extract_text() for p in pypdf.PdfReader(stream).pages if p.extract_text()])

def extract_text_from_excel(stream):
    df = pd.read_excel(stream, sheet_name=None)
    full_text = []
    for sheet_name, sheet_df in df.items():
        full_text.append(f"--- Sheet: {sheet_name} ---\n")
        full_text.append(sheet_df.to_string(index=False))
    return "\n".join(full_text)

@app.post("/process/")
async def process_file(info: ProcessInfo):
    temp_path = f"temp/{info.filename}"
    file_obj = BytesIO()
    s3_client.download_fileobj(BUCKET_NAME, temp_path, file_obj)
    file_obj.seek(0)

    extracted_text = ""
    
    # Check for images first and send to OCR
    if info.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        try:
            requests.post(f"http://module-c:8000/ocr/", json={"filename": info.filename, "source": info.source})
            return {"message": "Image file sent to OCR service for processing."}
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Could not connect to Module C (OCR): {e}")

    # Try to process as a text-based document
    try:
        if info.filename.lower().endswith('.docx'):
            extracted_text = extract_text_from_docx(file_obj)
        elif info.filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_obj)
        elif info.filename.lower().endswith(('.xls', '.xlsx')):
            extracted_text = extract_text_from_excel(file_obj)
        else:
             extracted_text = file_obj.read().decode('utf-8')

        # If PDF extraction yields no text, it must be a scanned PDF. Fallback to OCR.
        if info.filename.lower().endswith('.pdf') and not extracted_text.strip():
            requests.post(f"http://module-c:8000/ocr/", json={"filename": info.filename, "source": info.source})
            return {"message": "Scanned PDF detected, sent to OCR service."}

    except Exception as e:
        # If any conversion fails, move to NonConverted folder and stop
        department = "Uncategorized"
        non_converted_path = f"{department}/{info.source}/NonConverted/{info.filename}"
        s3_client.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': temp_path}, Key=non_converted_path)
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=temp_path)
        # Also save a record in the database
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port="5432")
        with conn.cursor() as cur:
            cur.execute("INSERT INTO documents (filename, source, storage_path, department, doc_type) VALUES (%s, %s, %s, %s, %s)", (info.filename, info.source, non_converted_path, department, 'Non-Converted'))
        conn.commit()
        conn.close()
        return {"message": f"File could not be converted: {e}"}

    # Translate the text
    trans_response = requests.post("http://module-g:8000/translate/", json={"text": extracted_text})
    trans_response.raise_for_status()
    final_text = trans_response.json().get("translated_text", extracted_text)

    # Analyze the final text
    analysis_response = requests.post("http://module-d:8000/analyze", json={"text": final_text})
    analysis = analysis_response.json()
    department = analysis.get('department', {}).get('label', 'Uncategorized')
    doc_type = analysis.get('doc_type', {}).get('label', 'Unknown')

    # Create final storage paths
    original_path = f"{department}/{info.source}/Original/{info.filename}"
    converted_path = f"{department}/{info.source}/Converted/{os.path.splitext(info.filename)[0]}.txt"

    # Move original file and save converted text
    s3_client.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': temp_path}, Key=original_path)
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=temp_path)
    s3_client.put_object(Bucket=BUCKET_NAME, Key=converted_path, Body=final_text.encode('utf-8'))

    # Save metadata to database
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port="5432")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO documents (filename, source, storage_path, department, doc_type) VALUES (%s, %s, %s, %s, %s)", (info.filename, info.source, original_path, department, doc_type))
    conn.commit()
    conn.close()
    
    return {"message": "File processed, translated, and stored successfully."}


