# app/ingest.py
from datetime import datetime

from app.drive_client import list_files, download_file
from app.extraction import extract_text
from app.chunking import chunk_text
from app.embeddings import embed_text
from app.vector_store import file_already_indexed, delete_file_chunks, upsert_chunk


def sync_project(drive_service, supabase_client, openai_client, project_id: str, folder_id: str) -> dict:
    indexed = []
    skipped = []

    for file_meta in list_files(drive_service, folder_id):
        modified_time = datetime.fromisoformat(file_meta["modifiedTime"].replace("Z", "+00:00"))

        if file_already_indexed(supabase_client, project_id, file_meta["id"], modified_time):
            skipped.append(file_meta["name"])
            continue

        delete_file_chunks(supabase_client, project_id, file_meta["id"])

        raw_bytes = download_file(drive_service, file_meta["id"])
        text = extract_text(raw_bytes, file_meta["mimeType"])

        for chunk in chunk_text(text):
            embedding = embed_text(openai_client, chunk)
            upsert_chunk(
                supabase_client,
                project_id=project_id,
                source_file_id=file_meta["id"],
                source_file_name=file_meta["name"],
                source_modified_time=modified_time,
                chunk_text=chunk,
                embedding=embedding,
            )

        indexed.append(file_meta["name"])

    return {"indexed": indexed, "skipped": skipped}
