FROM tensorflow/tensorflow 
WORKDIR /usr/app
COPY ./extractors/requirements.txt ./ 

RUN pip install -r requirements.txt

COPY ./extractors/extractor_server.py app.py
COPY ./extractors/extractors.py extractors.py
COPY ./utilities/utilities.py utilities.py

COPY ./extractors/templates/index.html ./templates/index.html
RUN mkdir tmp 

EXPOSE 5000
# CMD [ "python3", "extractor_server.py"]
CMD ["gunicorn" , "--workers=4", "--worker-class=gevent", "--worker-connections=1000", "--bind", "0.0.0.0:5000", "app:app"]