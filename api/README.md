# esp32-cambridge-transit-api

FastAPI-based aggregation API for Cambridge transit ESP32 project. This is an extremely simple webserver - not built for high throughput (e.g. it doesn't cleanly horizontally scale atm).

Transit information is requested on-demand from the upstream APIs and held in memory for a configurable time to minimize outbound requests.

## Quick start

Virtual environments and dependencies are managed by [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run fastapi dev # or `uv run fastapi start` for prod
```

### Environment vars

You'll also need to set a few environment variables. For local development, you can do this by creating a `.env` file adjacent to this README that looks like this:

```bash
BUS_STOP_REF=... # e.g. XYZ123
TRAIN_QUERY=... # e.g. KGX?filterCrs=SSD
TRAIN_API_KEY=...
```
