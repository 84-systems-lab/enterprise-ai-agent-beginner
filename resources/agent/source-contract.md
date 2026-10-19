# One contract for knowledge and MCP tools

An adapter supplies source_id, description, fetch(query, fallback), source_types
and max_items. The agent passes an empty fallback: each outer read has one
focused query. Source authentication stays inside its authorised adapter.

fetch returns evidence (a list), truncated (a boolean) and optional input_tokens
and output_tokens counters. Each evidence item contains chunk_text, source_name,
source_type, source_uri, object_key, location (an object) and similarity (a finite
number or null). A source URI identifies a source; it is not an access grant.

Before registering another source, demonstrate input validation, intended-user
access, a known fact, no-match, denied access, an unavailable result, bounded
output and correct provenance. Keep the existing read-only source catalogue
fixed until the new adapter and its tests pass. Never install a tool by accepting
an endpoint, command, token or query language from a model response.

AWS stores shared document passages. SharePoint reads delegated live documents.
Salesforce's adapter uses a protected backend route and an MCP session with the
connected user's grant. Their retrieval mechanics differ; their evidence can
enter the same agent loop without copying all three sources into one database.
