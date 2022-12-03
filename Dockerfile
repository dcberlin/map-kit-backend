FROM python:3.10.5-slim

ARG ENV
COPY . /app
WORKDIR /app

RUN : \
  && apt-get update \
  && apt-get install -y curl gdal-bin libgdal-dev netcat \
  && pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir poetry~=1.4.0 \
  && pip install gunicorn \
  && poetry config virtualenvs.create false \
  && :

RUN if [ "$ENV" = "development" ]; then \
  poetry install; \
else \
  poetry install --no-dev; \
  pip uninstall --yes poetry; \
fi

RUN python /app/src/manage.py collectstatic

ENTRYPOINT ["/app/scripts/entrypoint"]
CMD ["/app/scripts/run"]
