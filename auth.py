"""
auth.py — User signup, login, and JWT helpers.
Users are stored in data/users.json (no database needed).
"""

import json
import os
import time
from pathlib import Path

import bcrypt
import jwt
import streamlit as st

# ── Config ────────────────────────────────────────────────────
DATA_FILE  = Path(__file__).parent / "data" / "users.json"

def _get(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

JWT_SECRET = _get("JWT_SECRET", "math_tutor_secret_2024")
JWT_EXPIRY = 7 * 24 * 3600


# ── File helpers ──────────────────────────────────────────────

def _read_users() -> list:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("[]")
    return json.loads(DATA_FILE.read_text())


def _write_users(users: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(users, indent=2))


# ── Auth functions ────────────────────────────────────────────

def signup(name: str, email: str, password: str) -> dict:
    """
    Create a new user. Returns {"ok": True, "token": ..., "user": ...}
    or {"ok": False, "error": ...}.
    """
    name     = name.strip()
    email    = email.strip().lower()
    password = password.strip()

    if not name or not email or not password:
        return {"ok": False, "error": "All fields are required."}
    if len(password) < 6:
        return {"ok": False, "error": "Password must be at least 6 characters."}

    users = _read_users()
    if any(u["email"] == email for u in users):
        return {"ok": False, "error": "An account with this email already exists."}

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user   = {"id": str(int(time.time() * 1000)), "name": name, "email": email, "password": hashed}
    users.append(user)
    _write_users(users)

    token = _create_token(user)
    return {"ok": True, "token": token, "user": {"id": user["id"], "name": name, "email": email}}


def login(email: str, password: str) -> dict:
    """
    Verify credentials. Returns {"ok": True, "token": ..., "user": ...}
    or {"ok": False, "error": ...}.
    """
    email    = email.strip().lower()
    password = password.strip()

    if not email or not password:
        return {"ok": False, "error": "Email and password are required."}

    users = _read_users()
    user  = next((u for u in users if u["email"] == email), None)

    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return {"ok": False, "error": "Invalid email or password."}

    token = _create_token(user)
    return {"ok": True, "token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}}


def verify_token(token: str) -> dict | None:
    """
    Decode and verify a JWT. Returns the payload dict or None if invalid.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


# ── Internal ──────────────────────────────────────────────────

def _create_token(user: dict) -> str:
    payload = {
        "id":    user["id"],
        "name":  user["name"],
        "email": user["email"],
        "exp":   int(time.time()) + JWT_EXPIRY,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
