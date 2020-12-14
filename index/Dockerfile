FROM tensorflow/tensorflow

WORKDIR /usr/app

COPY ./index/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./index/index_server.py app.py
COPY ./index/index.py index.py
COPY ./utilities/utilities.py utilities.py

EXPOSE 5000

CMD ["gunicorn" , "--workers=4", "--worker-class=gevent", "--worker-connections=1000", "--bind", "0.0.0.0:5000", "app:app"]