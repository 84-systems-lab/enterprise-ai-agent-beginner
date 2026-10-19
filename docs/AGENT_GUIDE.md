# Create and inspect the knowledge agent

The shared runtime is [tool_agent.py](../app/shared/askanydoc_rag/tool_agent.py).
It receives a model client, task, server-registered adapters and selected source
IDs. It validates read proposals, bounds evidence and model/tool calls, builds
citations from provenance and returns source coverage plus safe activity.

The application wrapper is [enterprise_agent.py](../app/api/enterprise_agent.py).
The protected job API validates mode/sources and owner identity; the worker
revalidates and dispatches; the React browser shows Agent mode, source choices,
citations and activity. Sources narrow the catalogue, never grant access.

After the small learning/ exercises in Chapters 1-4, use the standard-library [agent demo](../tools/agent_app_demo.py). Its
model is scripted; its loop and fixture adapters execute. After installing the
development lock, run [mcp_agent_demo.py](../tools/mcp_agent_demo.py), then repeat
with --agent. These use a real supplied local stdio server and fictional data.
The model in that agent demonstration remains scripted.

[agent_starter.py](../resources/agent/agent_starter.py) composes a live AWS
knowledge agent using the same runtime. Follow Chapter 11 prerequisites, identity,
model and cost checks before running it. For the browser, use the existing
deployment and user-authorised SharePoint/Salesforce adapters; never insert a
service-account credential to bypass a provider permission test.

Use the [design worksheet](../resources/agent/agent-design.md) and
[source contract](../resources/agent/source-contract.md) when adapting the task.
Run tools/check.py, tools/source_tests.py api and the frontend request tests.
Default limits are four outer reads and six model turns. The knowledge agent
cannot perform business writes and uses a new question context for each task.
Activity is returned with the completed answer, not streamed as live progress.
