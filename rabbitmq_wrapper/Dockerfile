FROM python:3.8.6-alpine3.12 
WORKDIR /usr/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY server.py server.py
COPY publisher.py publisher.py

EXPOSE 5000 
CMD [ "python3", "-u", "server.py"]