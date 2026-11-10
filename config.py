import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")

    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:3b")

    LLM_BASE_URL = os.environ.get(
        "LLM_BASE_URL",
        "http://localhost:11434"
    )