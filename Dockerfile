FROM python:alpine

RUN touch /IS_CONTAINER

WORKDIR /home

COPY *.py ./
ADD bot bot

RUN mkdir data plugins
RUN ln -s /home/data /
RUN ln -s /home/plugins /

RUN python3 setup.py

VOLUME [ "/data", "/plugins" ]

ENTRYPOINT [ "python3", "main.py" ]
