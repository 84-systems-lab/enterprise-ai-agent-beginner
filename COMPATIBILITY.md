# Edition tool selections

Recorded October 2026. Use the locks supplied with this edition before attempting
a package upgrade. These selections describe different roles in the build.

| Component | Selection |
|---|---|
| Command examples | Windows with PowerShell 7 throughout; explicit .venv interpreter paths |
| Local Python | Python 3.12; local checks used 3.12.14 and a fresh 3.12.10 venv |
| Node / npm | Node 24; checked 24.19.0 and fresh 24.15.0 installs with npm 11.12.1 |
| Frontend | React/Vite/MSAL graph in frontend/package-lock.json |
| Terraform | >=1.5 and <2.0, matching infra/main.tf; local static checks used 1.16.2 |
| Providers | AWS 5.100.0 and archive 2.8.0 in provider lock |
| Lambda ZIP/container target | Python 3.13, Linux x86_64 |
| Embeddings | amazon.titan-embed-text-v2:0, 1024 dimensions, normalised |
| Main answer example | AU Claude Haiku 4.5 profile, Converse/tool use/JSON |
| Vector store | Aurora PostgreSQL with pgvector and enabled Data API |
| SharePoint path | Delegated Graph Search and bounded PDF extraction |
| Agent runtime | Explicit Bedrock Converse loop; no new framework |
| MCP SDK | 1.30.0 in both Python locks; use its 1.x API |
| Local MCP lesson | stdio child process, structured policy result, scripted-model agent |
| Salesforce path | ECA, named-user OAuth and SObject Reads Hosted MCP |

Local Python tests use controlled service responses. The fixture browser uses
standard-library Python. Before deploying, the documented container/import
commands check the target platform and the chapter checkpoints check your live
account, tenant and org. A successful local test is not a live permission result.

requirements-dev.lock pins the local development graph. requirements-cloud.lock
pins the deployment graph without Windows-only/test-only packages. The Linux
build must use compatible wheels, not packages copied from a Windows environment.

Service availability, billing, consent policies and supported model profiles can
change. Consult the official references and verify the saved setting/result.
