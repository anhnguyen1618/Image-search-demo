FROM tensorflow/tensorflow

WORKDIR /usr/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY index_server.py index_server.py
COPY index.py index.py

EXPOSE 9000

CMD [ "python3", "index_server.py"]