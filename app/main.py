# app/main.py
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from supabase import create_client

from app import config
from app.drive_client import build_drive_service
from app.ingest import sync_project
from app.embeddings import embed_text
from app.vector_store import search_chunks

AUTO_SYNC_PROJECT_ID = "demo-project"
AUTO_SYNC_INTERVAL_SECONDS = 15


async def auto_sync_loop():
    while True:
        try:
            result = sync_project(
                drive_service=get_drive_service(),
                supabase_client=get_supabase_client(),
                openai_client=get_openai_client(),
                project_id=AUTO_SYNC_PROJECT_ID,
                folder_id=config.DRIVE_FOLDER_ID,
            )
            if result["indexed"]:
                print(f"[auto-sync] indexed: {result['indexed']}")
        except Exception as exc:
            print(f"[auto-sync] error: {exc}")
        await asyncio.sleep(AUTO_SYNC_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(auto_sync_loop())
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)


def get_drive_service():
    return build_drive_service(config.GOOGLE_SERVICE_ACCOUNT_FILE)


def get_supabase_client():
    return create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)


def get_openai_client():
    return OpenAI(api_key=config.OPENAI_API_KEY)


class AskRequest(BaseModel):
    project_id: str
    question: str


@app.post("/sync")
def sync(project_id: str):
    drive_service = get_drive_service()
    supabase_client = get_supabase_client()
    openai_client = get_openai_client()
    return sync_project(
        drive_service=drive_service,
        supabase_client=supabase_client,
        openai_client=openai_client,
        project_id=project_id,
        folder_id=config.DRIVE_FOLDER_ID,
    )


@app.post("/ask")
def ask(request: AskRequest):
    supabase_client = get_supabase_client()
    openai_client = get_openai_client()

    query_embedding = embed_text(openai_client, request.question)
    results = search_chunks(supabase_client, project_id=request.project_id, query_embedding=query_embedding)

    if not results:
        return {"results": [], "message": "No relevant source found for this project."}

    return {"results": results}
