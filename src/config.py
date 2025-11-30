import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Base Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Data Files
    SALES_DATA = DATA_DIR / "sales.csv"
    SUPPORT_DATA = DATA_DIR / "support.csv"
    MARKETING_DATA = DATA_DIR / "marketing.csv"
    
    # Output Files
    SLACK_LOGS = BASE_DIR / "slack_logs.json"
    MEMORY_FILE = BASE_DIR / "memory.json"
    TASKS_FILE = BASE_DIR / "tasks.json"
    REPORT_FILE = BASE_DIR / "report.pdf"
    CHROMA_DB_DIR = DATA_DIR / "chroma_db"

    # Environment Variables
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
    DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    TO_EMAIL = os.getenv("TO_EMAIL")

    @classmethod
    def ensure_dirs(cls):
        """Ensure necessary directories exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
