
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
# DB path
DB_PATH ="data/edumind.db"
CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")

# LLM definitions
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

#   (Guardrails)
PARENT_BLOCKED_KEYWORDS = ["class_average", "compare_students", "all_grades", "class", "students"]

# Session definitions
SESSION_EXPIRY_MINUTES = 30

#Access token
ACCESS_TOKEN_EXPIRE_MINUTES=60 * 24
SECRET_KEY = os.getenv("SECRET_KEY", "temporary-insecure-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


