# Build Your First AI Agent with Python - companion

A Practical Beginner's Guide to Building a Complete Enterprise Assistant with RAG and MCP.

Start with Chapter 1. This edition is designed for first-semester IT students.
The book explains files, editor, terminal and Python before APIs or cloud setup.
Use PowerShell 7 on Windows x64 and Python 3.12 for the documented local route.

## First small program

From this extracted companion root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe learning/hello.py
```

Chapter 1 has you create your own hello.py under local-records. The supplied
learning/ modules are complete small checkpoints for Chapters 1-4. Run module
examples from this root, for example -m learning.search damaged. No cloud account
or model request is needed for those lessons.

## Source version and book resources

This is the complete source snapshot for the beginner book. Keep an unchanged
archive and record the version used for your build. Visit the
[84 Systems Lab book website](https://84-systems-lab.github.io/) for complete
downloads, all twelve chapter packs and checksums. Browse the
[GitHub source](https://github.com/84-systems-lab/enterprise-ai-agent-beginner).
The [original first-edition code snapshot](https://github.com/84-systems-lab/enterprise-ai-agent-beginner/tree/7f1b8ba16694bddb71353fef5e6c01c66df290a8)
preserves the starting code. A GitHub repository's
newest default branch may accompany a later edition; choose the version named
for your book. The supplied ZIP is sufficient to begin without Git experience.
Extract updates into a new folder rather than over your configured project.

Appendix B also has a topic finder and discussions for the twelve optional
chapter questions. The small-file reference solutions are in
[resources/learning-solutions](resources/learning-solutions). Try your own file
first, then compare the input, decision and result with the supplied solution.

## Grow the project

Follow [BUILD_ORDER.md](BUILD_ORDER.md). The first four chapters cover Python,
evidence, tools, a scripted loop and real local MCP. Chapter 5 introduces the
browser/API and sign-in; Chapter 6 deploys the cloud foundation; Chapter 7 builds
the knowledge store in schema/upload/retrieval order. Chapters 8-12 maintain,
connect, guide and evaluate the complete application.

Install requirements-dev.lock in .venv at the Chapter 4 MCP step. The application
uses indexed AWS documents, delegated live SharePoint retrieval and user-linked
Salesforce MCP reads. These are examples of knowledge-source patterns with
separate permissions. The application agent is bounded and read-only.

- [Deployment](DEPLOYMENT.md) is a command-oriented checklist, not an unattended script.
- [Compatibility](COMPATIBILITY.md) records selected versions and locks.
- resources/chapter-01 through chapter-12 contain worksheets and command excerpts.
- resources/agent contains a live entry-point starter and contract worksheet.
- [Notices](NOTICE.md) and notices/ contain dependency information.

Keep your own notes in ignored local-records. Do not publish filled .env/tfvars,
credentials, active grants, Terraform state or private documents. The distributed
fixtures are fictional; real service accounts and access belong to the reader.

Run local checks with tools/check.py and -m learning.check_lessons. Source tests
are selected with tools/source_tests.py. The book distinguishes controlled local
checks, real local MCP and the live account/model checks you perform later.

Additional maps: [Architecture](docs/ARCHITECTURE.md), [Agent guide](docs/AGENT_GUIDE.md), [Configuration](docs/CONFIGURATION.md) and [Resources](docs/RESOURCE_MAP.md).
