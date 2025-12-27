FROM python:3.13.11-alpine

COPY . .
RUN pip install .

EXPOSE 8000

CMD [ "fastapi", "run" ]