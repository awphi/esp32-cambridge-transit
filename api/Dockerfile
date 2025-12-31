FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY app app
COPY uv.yaml uv.yaml
COPY pyproject.toml pyproject.toml
COPY .python-version .python-version
RUN uv sync --frozen

EXPOSE 8000

CMD [ "uv", "run", "fastapi", "run" ]