FROM python:alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

WORKDIR /app

RUN mkdir /data /plugins
RUN touch /IS_CONTAINER

RUN adduser -D farzin

COPY . .

RUN chmod +x ./docker-entrypoint.sh
RUN chown -R farzin:farzin /app

VOLUME ["/data", "/plugins"]

USER farzin

RUN python setup.py

ENTRYPOINT ["/app/docker-entrypoint.sh"]

CMD ["python3", "main.py"]
