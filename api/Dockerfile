FROM ubuntu:24.04

ENV PATH="${PATH}:/root/.local/bin"

RUN apt update
RUN apt install pipx -y
RUN pipx ensurepath
RUN pipx install poetry
RUN pipx install poethepoet

COPY . .

RUN poetry install

EXPOSE 8000


CMD [ "poe", "start" ]