
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = os.path.join(BASE_DIR, "data")
# DB path
DB_PATH ="data/edumind.db"
CHROMA_PATH = os.path.join(DATA_DIR, "chroma_db")

# LLM definitions
OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_BASE_URL = "http://localhost:11434"

#   (Guardrails)
PARENT_BLOCKED_KEYWORDS = ["class_average", "compare_students", "all_grades", "class", "students"]

# Session definitions
SESSION_EXPIRY_MINUTES = 30

