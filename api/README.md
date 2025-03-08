# esp32-cambridge-transit-api

FastAPI-based aggregation API for Cambridge transit ESP32 project

## Quick start

Virtual environments and dependencies are managed by [poetry](https://python-poetry.org/docs/), running tasks is done via [poe the poet](https://poethepoet.natn.io/index.html). Recommended to install both of these via [pipx](https://pipx.pypa.io/stable/).

```sh
poetry install
poe dev # or `poe start` for prod
```

### Environment vars

You'll also need to set a few environment variables. For local development, you can do this by creating a `.env` file adjacent to this README that looks like this:

```bash
BUS_STOP_REF=...
```
