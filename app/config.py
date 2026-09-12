import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"]
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]
