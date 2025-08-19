# ProjectOtto

ProjectOtto is an autonomous AI research agent framework that utilizes the internet to collect and synthesize up-to-date data on any topic. It is built with [Pydantic AI](https://github.com/pydantic/pydantic-ai) and designed to be lightweight enough to run on devices like a Raspberry Pi, while also being scalable into a fully modular research service.

## Features

- Real-time internet search via DuckDuckGo tool integration
- Structured logging of tool execution for auditing and analysis
- Modular toolset architecture using `FunctionToolset` and `WrapperToolset`
- Concept for persistent topic-based agents
- Planned cron job automation and Discord webhooks
- Future support for FastAPI dashboards and full persistence