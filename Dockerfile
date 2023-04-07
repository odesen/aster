# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim as build

RUN apt-get update && \
    apt-get install -y libpq-dev

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

FROM python:3.11-slim as runtime

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y libpq5

ARG ASTER_VERSION
ARG ASTER_REVISION
ENV ASTER_VERSION=${ASTER_VERSION:-unknown}
ENV ASTER_REVISION=${ASTER_REVISION:-unknown}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY ./src/aster /app/aster
COPY ./alembic /app/alembic
COPY ./alembic.ini /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

ENTRYPOINT [ "python", "-m", "aster" ]

CMD [ "--help" ]
