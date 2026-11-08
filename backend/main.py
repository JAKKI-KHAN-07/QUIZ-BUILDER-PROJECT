
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import PyPDF2
from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    File,
    Header,
    HTTPException,
    UploadFile,
    status,
)
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from models import QuizRequest
from quiz_generator import generate_quiz, generate_quiz_from_text


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = BASE_DIR / "quiz_builder.db"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="AI Quiz Builder API", version="1.0.0")


# --------------------------------------------------
# Database
# --------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


initialize_database()


# --------------------------------------------------
# Request schemas
# --------------------------------------------------

class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=72)


class SigninRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=1, max_length=72)


# --------------------------------------------------
# Authentication helpers
# --------------------------------------------------

def create_access_token(user_id: int, email: str) -> str:
    if len(JWT_SECRET_KEY) < 32:
        raise RuntimeError(
            "Set JWT_SECRET_KEY to a random secret of at least "
            "32 characters in backend/.env."
        )

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def get_current_user(
    authorization: str | None = Header(default=None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Please sign in first.",
        )

    token = authorization.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please sign in again.",
        )

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found.")

    return dict(user)


# --------------------------------------------------
# Home and health
# --------------------------------------------------

@app.get("/")
def home():
    return {"message": "AI Quiz Builder API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# Signup
# --------------------------------------------------

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest):
    name = data.name.strip()
    email = data.email.strip().lower()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Please enter your full name.",
        )

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(
            status_code=422,
            detail="Please enter a valid email address.",
        )

    password_hash = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users
                    (name, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password_hash,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="This email is already registered. Please sign in.",
        )

    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Could not save your account to the database.",
        )

    try:
        token = create_access_token(user_id, email)
    except RuntimeError as exc:
        # The account is saved, but the server needs its JWT secret
        # configured before it can issue a login token.
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "message": "Account created successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
        },
    }


# --------------------------------------------------
# Signin
# --------------------------------------------------

@app.post("/signin")
def signin(data: SigninRequest):
    email = data.email.strip().lower()

    with get_connection() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    try:
        password_matches = bcrypt.checkpw(
            data.password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )
    except (ValueError, TypeError):
        password_matches = False

    if not password_matches:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    try:
        token = create_access_token(user["id"], user["email"])
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "message": "Signed in successfully.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


# --------------------------------------------------
# Current user
# --------------------------------------------------

@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user


# --------------------------------------------------
# Generate quiz from a topic
# --------------------------------------------------

@app.post("/generate-quiz")
def create_quiz(data: QuizRequest):
    try:
        quiz = generate_quiz(
            data.topic,
            data.difficulty,
            data.num_questions,
        )
        return {"quiz": quiz}

    except Exception as exc:
        print("Quiz generation error:", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Quiz generation failed: {exc}",
        )


# --------------------------------------------------
# Generate quiz from PDF or TXT
# --------------------------------------------------

@app.post("/upload-quiz")
async def upload_quiz(
    file: UploadFile = File(...),
    difficulty: str = "Medium",
    num_questions: int = 10,
):
    if difficulty not in {"Easy", "Medium", "Hard"}:
        raise HTTPException(
            status_code=422,
            detail="Difficulty must be Easy, Medium, or Hard.",
        )

    if not 1 <= num_questions <= 20:
        raise HTTPException(
            status_code=422,
            detail="Number of questions must be between 1 and 20.",
        )

    filename = (file.filename or "").lower()

    try:
        if filename.endswith(".txt"):
            content = await file.read()
            text_data = content.decode("utf-8-sig", errors="replace")

        elif filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file.file)
            text_data = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported.",
            )

        if not text_data.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the file.",
            )

        quiz = generate_quiz_from_text(
            text_data,
            difficulty,
            num_questions,
        )

        return {"quiz": quiz}

    except HTTPException:
        raise

    except Exception as exc:
        print("Upload error:", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Quiz generation failed: {exc}",
        )

    finally:
        await file.close()
