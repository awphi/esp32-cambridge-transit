# esp32-cambridge-transit-api

FastAPI-based aggregation API for Cambridge transit ESP32 project

## Quick start

Virtual environments and dependencies are managed by [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run fastapi dev # or `uv run fastapi start` for prod
```

### Environment vars

You'll also need to set a few environment variables. For local development, you can do this by creating a `.env` file adjacent to this README that looks like this:

```bash
BUS_STOP_REF=...
```
