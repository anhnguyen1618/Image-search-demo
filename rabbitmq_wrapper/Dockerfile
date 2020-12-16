FROM tiangolo/meinheld-gunicorn-flask:python3.7-2019-10-15
WORKDIR /usr/app

COPY ./rabbitmq_wrapper/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./rabbitmq_wrapper/server.py app.py
COPY ./rabbitmq_wrapper/publisher.py publisher.py
COPY ./utilities/utilities.py utilities.py

EXPOSE 5000 

CMD ["gunicorn" , "--workers=4", "--worker-class=gevent", "--worker-connections=1000", "--bind", "0.0.0.0:5000", "app:app"]