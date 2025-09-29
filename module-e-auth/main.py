import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
import psycopg2
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
import boto3 # New import

# ... (keep your SECRET_KEY, ALGORITHM, etc. configuration) ...
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# ... (keep your CORS middleware setup) ...
origins = ["http://localhost:5173"]
app.add_middleware(...) # KEEP YOUR FULL CORS MIDDLEWARE CODE

# --- MinIO Configuration ---
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "documents"
s3_client = boto3.client("s3", endpoint_url=f"http://{MINIO_ENDPOINT}", aws_access_key_id=MINIO_ACCESS_KEY, aws_secret_access_key=MINIO_SECRET_KEY)


# --- Security and Password Hashing ---
# This is for checking the user's password against the hash in the DB
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# --- CORS Middleware ---
# This allows your frontend (running on port 5173) to talk to this backend.
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Connection ---
# This is correct ✅
def get_db_connection():
    conn = psycopg2.connect(
        dbname="kmrl_docs",
        user="admin",
        password="admin",
        host="postgres", # <--- Use the service name from docker-compose.yml
        port="5432"
    )
    return conn

# --- Helper Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    """Looks up a user in the database by their username."""
    with db.cursor() as cur:
        cur.execute("SELECT username, password_hash, role FROM users WHERE username = %s", (username,))
        user_record = cur.fetchone()
        if user_record:
            return {"username": user_record[0], "password_hash": user_record[1], "role": user_record[2]}
    return None

def create_access_token(data: dict):
    """Creates a secure login token (JWT)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/documents")
async def get_documents(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    This is a protected endpoint. It requires a valid login token.
    It fetches all document records from the database.
    """
    conn = get_db_connection()
    documents = []
    with conn.cursor() as cur:
        cur.execute("SELECT id, filename, source, department, doc_type, processed_at FROM documents ORDER BY processed_at DESC")
        for row in cur.fetchall():
            documents.append({
                "id": row[0],
                "filename": row[1],
                "source": row[2],
                "department": row[3],
                "doc_type": row[4],
                "processed_at": row[5].strftime("%Y-%m-%d %H:%M")
            })
    conn.close()
    return documents

# --- API Endpoints ---
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """This is the main login endpoint."""
    conn = get_db_connection()
    user = get_user(conn, form_data.username)
    conn.close()

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/files/{department}/{folder_type}")
async def list_files(department: str, folder_type: str, token: Annotated[str, Depends(oauth2_scheme)]):
    """Lists files from a specific folder in MinIO for a given department."""
    prefix = f"{department}/{folder_type}/"
    files_to_return = []
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if 'Contents' in response:
            for item in response['Contents']:
                # Generate a temporary, secure URL to download the file
                url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': BUCKET_NAME, 'Key': item['Key']},
                                                        ExpiresIn=3600) # URL is valid for 1 hour

                files_to_return.append({
                    "name": os.path.basename(item['Key']),
                    "url": url,
                    "size": item['Size']
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return files_to_return


# ADD THIS NEW ENDPOINT TO module-e-auth/main.py

@app.get("/departments")
async def get_departments(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Protected endpoint to get a list of all unique departments that have documents.
    """
    # We could add a check here to ensure only admins can call this
    # For now, any logged-in user can see the list.
    conn = get_db_connection()
    departments = []
    with conn.cursor() as cur:
        # Select the unique department names from the documents table
        cur.execute("SELECT DISTINCT department FROM documents ORDER BY department")
        for row in cur.fetchall():
            departments.append(row[0])
    conn.close()
    return departments



@app.get("/")
def root():
    return {"message": "Module E - Authentication service is running!"}

