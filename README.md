# Document retrieval with Google Drive and pgvector

A Python proof of concept for finding relevant passages in a small document collection. It reads files from Google Drive, creates OpenAI embeddings, stores them in Supabase pgvector, and exposes a FastAPI retrieval API.

This is the retrieval part of a RAG system. The API returns source chunks, filenames, and similarity scores. It does not generate answers. It uses Google Drive, OpenAI, and Supabase, not AWS or Amazon Bedrock.

## What the code does

- Extracts text from TXT files and text-based PDFs, with Tesseract OCR for PNG and JPEG images.
- Splits text into overlapping, word-based chunks and embeds them with `text-embedding-3-small`.
- Reindexes new or changed files using Drive IDs and modification timestamps.
- Retrieves up to five similar chunks, filtered by a supplied `project_id`.

`POST /sync?project_id=demo-project` indexes the configured folder. `POST /ask` accepts a JSON question and returns matching source chunks. On server startup, a background task also polls the configured Drive folder every 15 seconds, using the fixed project ID `demo-project`.

## Status and boundaries

This is a local demonstration, not a production service or a completed client deployment. Its endpoints have no authentication. Project IDs filter data but do not provide access control. The SQL schema does not enable row-level security, and the application uses a Supabase service-role key.

Run it on loopback only. Do not expose it through a public tunnel or deploy it publicly without adding authentication, authorization, and other security controls. Starting the server can immediately send document text to OpenAI and write to Supabase. Changed or new documents can incur embedding costs. Stop the server to stop background polling. See [SECURITY.md](SECURITY.md).

There is no answer-generation layer, user interface, AWS deployment, or saved Custom GPT configuration in this repository. The sample-document generator creates fictional material. Do not use private or client documents for a public demonstration.

## Local setup

The existing tests were checked with Python 3.14.6 and the package versions in `requirements.txt`. The new CI workflow targets Python 3.12; a fresh installation and the hosted CI run have not yet been verified.

1. Create an environment and install the Python dependencies:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

2. Install the Tesseract executable if you want to ingest images. `pytesseract` alone does not install the OCR engine.
3. Create a dedicated demo Supabase project and apply `sql/schema.sql` in its SQL editor. Do not apply demo setup to a production database.
4. Enable the Google Drive API for a demo Google Cloud project. Create a service account, save its credentials locally as `service-account.json`, and share only the intended demo folder with that service account.
5. Copy `.env.example` to `.env` and replace every placeholder:

   ```sh
   cp .env.example .env
   ```

   - `OPENAI_API_KEY`: an API key with access to the embedding model.
   - `SUPABASE_URL`: the dedicated demo project's URL.
   - `SUPABASE_SERVICE_KEY`: its service-role key, never a browser-side value.
   - `GOOGLE_SERVICE_ACCOUNT_FILE`: path to the local service-account JSON file.
   - `DRIVE_FOLDER_ID`: the folder shared with that service account.

6. Optionally generate fictional sample files and upload them manually into the demo Drive folder:

   ```sh
   .venv/bin/python scripts/create_fake_docs.py
   ```

7. Start the server locally. This also starts background indexing:

   ```sh
   .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

The API documentation is available at `http://127.0.0.1:8000/docs` while the server runs.

## Try the API

Use the same project ID as the background task for this single-folder demo:

```sh
curl -X POST 'http://127.0.0.1:8000/sync?project_id=demo-project'

curl -X POST 'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{"project_id":"demo-project","question":"Who signed the waiver?"}'
```

Retrieval returns a `results` array with `source_file_name`, `chunk_text`, and `similarity`. The no-source message is returned only when the search yields no rows. There is no minimum relevance threshold.

## Offline unit tests

```sh
.venv/bin/python -B scripts/run_offline_tests.py
```

The runner replaces all service settings with dummy values, disables socket connections, and runs pytest without bytecode or pytest-cache output. No API keys, database, Drive account, or Tesseract executable are needed for these tests. Installing dependencies still requires package downloads unless they are already available locally.

The clean publication copy passed 15 unit tests. These cover chunking, plain-text extraction, mocked service calls, ingestion decisions, and API responses. They do not verify live service integration, OCR/PDF accuracy, SQL execution, or the background task lifecycle.

`.github/workflows/tests.yml` is newly added publication support. It runs the same offline test command after dependency installation. It is not evidence of historical CI or a successful hosted run.

## Known limitations

- Drive listing has no pagination or nested-folder traversal. Native Google Docs export is not implemented.
- Source-file deletion is not reconciled with stored chunks.
- Reindexing deletes old chunks before replacement succeeds and is not transactional. Unsupported or failed files can abort a sync.
- All requests use one configured Drive folder. Supplying another project ID does not select another folder or establish isolation.
- Background indexing uses synchronous service calls inside an async task. Concurrent sync requests are not coordinated.
- There is no retry policy, rate limiting, endpoint authentication, or relevance threshold.

No software license has been selected for this publication copy.
