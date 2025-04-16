FROM python:alpine

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --upgrade --no-cache-dir --break-system-packages \
    kurigram==v2.1.37 \
    python-dotenv==1.0.0 \
    sqlalchemy==2.0.36

WORKDIR /home

COPY main.py .
COPY config.py .
ADD bot bot

RUN mkdir data plugins
RUN ln -s /home/data /
RUN ln -s /home/plugins /

VOLUME [ "/data", "/plugins" ]

ENTRYPOINT [ "python3", "main.py" ]
