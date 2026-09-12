# tests/conftest.py
import os

os.environ.setdefault("OPENAI_API_KEY", "dummy-openai-key")
os.environ.setdefault("SUPABASE_URL", "https://dummy.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "dummy-supabase-key")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_FILE", "tests/fixtures/dummy_service_account.json")
os.environ.setdefault("DRIVE_FOLDER_ID", "dummy-folder-id")
