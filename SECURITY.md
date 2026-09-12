# Security notes

This repository is a local retrieval proof of concept. It has no authentication, authorization, or rate limiting. A supplied `project_id` is a query filter, not an access-control boundary. The supplied database schema does not enable row-level security. The Supabase service-role key must remain server-side.

Bind the server to `127.0.0.1`. Do not expose these endpoints through a public tunnel or use this code as a public service without adding and testing appropriate security controls. Do not load private or client documents into a publicly shared demonstration.

## Credentials and data

- Keep `.env` and service-account JSON files outside version control. The example environment file contains placeholders only.
- Use a dedicated demo database and Drive folder. Share only that folder with the service account.
- Review the exact files staged for publication. Ignore rules do not protect previously tracked files or Git history.
- Document text is sent to OpenAI for embeddings and stored in Supabase. Returned chunks expose source text and filenames.
- Starting the server immediately enables background polling every 15 seconds. New or changed files can trigger paid embedding requests and database writes without a manual `/sync` call.

If credentials are exposed, stop the demo and revoke or rotate them at their providers. Removing a file from a later commit does not remove it from Git history.

## Reliability limits that affect data

Reindexing deletes a file's stored chunks before extraction and embedding complete. A failure can leave missing or partial data. Deleted Drive files remain in the index until separately removed. Do not use this demo as the only copy of important data.

## Reporting an issue

Do not paste secrets, personal data, or client documents into public issues. Use GitHub private vulnerability reporting if it is enabled, or contact the repository owner privately before sharing sensitive details.

The offline unit suite uses dummy configuration and blocks socket connections. Passing it is not a security audit or a live-integration test.
