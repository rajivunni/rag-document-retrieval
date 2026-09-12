from datetime import datetime


def upsert_chunk(client, project_id, source_file_id, source_file_name, source_modified_time, chunk_text, embedding):
    client.table("document_chunks").insert({
        "project_id": project_id,
        "source_file_id": source_file_id,
        "source_file_name": source_file_name,
        "source_modified_time": source_modified_time.isoformat(),
        "chunk_text": chunk_text,
        "embedding": embedding,
    }).execute()


def search_chunks(client, project_id, query_embedding, match_count=5):
    response = client.rpc(
        "match_document_chunks",
        {"query_embedding": query_embedding, "match_project_id": project_id, "match_count": match_count},
    ).execute()
    return response.data


def file_already_indexed(client, project_id, source_file_id, source_modified_time) -> bool:
    response = (
        client.table("document_chunks")
        .select("source_modified_time")
        .eq("project_id", project_id)
        .eq("source_file_id", source_file_id)
        .execute()
    )
    if not response.data:
        return False
    indexed_time = datetime.fromisoformat(response.data[0]["source_modified_time"])
    return indexed_time >= source_modified_time


def delete_file_chunks(client, project_id, source_file_id):
    client.table("document_chunks").delete().eq("project_id", project_id).eq("source_file_id", source_file_id).execute()
