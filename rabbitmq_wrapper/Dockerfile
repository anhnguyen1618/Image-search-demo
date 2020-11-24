FROM python:3.8.6-alpine3.12 
WORKDIR /usr/app

COPY ./rabbitmq_wrapper/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./rabbitmq_wrapper/server.py server.py
COPY ./rabbitmq_wrapper/publisher.py publisher.py

EXPOSE 5000 
CMD [ "python3", "-u", "server.py"]