FROM ghcr.io/astral-sh/uv:python3.13-alpine

COPY . .
RUN uv sync --frozen

EXPOSE 8000

CMD [ "uv", "run", "fastapi", "run" ]