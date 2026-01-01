FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY app app
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
COPY .python-version .python-version
RUN uv sync --frozen

EXPOSE 8000

CMD [ "uv", "run", "fastapi", "run" ]