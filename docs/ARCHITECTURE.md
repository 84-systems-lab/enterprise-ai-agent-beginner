# Architecture

The React/Vite browser signs an employee in through MSAL. API Gateway validates
the Entra token before the Python API creates an owned answer job. SQS carries
work to a worker; DynamoDB stores a bounded, expiring result for that owner.

| Source | Retrieval path | Permission boundary |
|---|---|---|
| AWS documents | S3 upload -> extract -> chunk -> Titan V2 -> Aurora pgvector/Data API | Application-owned shared library and scoped AWS roles |
| SharePoint | Entra on-behalf-of -> delegated Graph Search -> bounded PDF extraction | Signed-in employee's Microsoft rights and approved sites |
| Salesforce | User-linked OAuth grant -> Hosted MCP SObject Reads -> bounded structured facts | Connected user's object, field and record rights |

The agent and guided controller receive bounded evidence and preserve source references
and per-source coverage. Live enterprise sources are not copied into the vector
index. Unknown citations fail validation; claim support is evaluated separately.

app/ holds runtime source; infra/ holds Terraform and SQL; frontend/ holds the
browser. app/shared/askanydoc_rag/tool_agent.py is the shared application agent.
lab/ contains offline contracts and a compact first example. tools/
contains local checks, MCP server/client lessons and explicit service probes.
resources/agent/ contains an entry-point starter and design worksheet. resources/ contains fictional
fixtures and reader worksheets. Full chapter explanations are in the book.
