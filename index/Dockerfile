FROM tensorflow/tensorflow

WORKDIR /usr/app

COPY ./index/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./index/index_server.py index_server.py
COPY ./index/index.py index.py

EXPOSE 9000

CMD [ "python3", "index_server.py"]