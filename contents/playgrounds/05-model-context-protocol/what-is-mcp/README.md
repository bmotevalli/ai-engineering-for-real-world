# Lesson 1 — What is Model Context Protocol?

This first lesson is deliberately dependency-free. It uses small Python dataclasses to make the MCP architectural boundary visible before later lessons introduce the real MCP SDK and a transport.

## Run

From `contents/`:

```bash
jupyter lab playgrounds/05-model-context-protocol/what-is-mcp/lesson-01-what-is-mcp.ipynb
```

## What to observe

1. A server declares tools, resources, and prompts.
2. A client discovers those capabilities for its host.
3. Discovery is metadata exchange, not authorisation.
4. A host-owned policy check controls whether a requested tool call can proceed.

## Key distinction

MCP standardises host-to-server integration. An LLM may later choose an MCP-discovered tool through function calling, but MCP does not turn the host into an agent or grant the tool permission to run.

## Companion material

- [Module 05 overview](../../../docs/module-05-model-context-protocol/index.html)
- [Detailed Lesson 1 page](../../../docs/module-05-model-context-protocol/lesson-01-what-is-mcp.html)
- [Official MCP specification](https://modelcontextprotocol.io/specification)
