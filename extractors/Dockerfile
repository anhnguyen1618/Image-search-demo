FROM tensorflow/tensorflow 
WORKDIR /usr/app
COPY ./requirements.txt ./ 

RUN pip install -r requirements.txt

COPY extractor_server.py extractor_server.py
COPY extractors.py extractors.py
COPY ./templates/index.html ./templates/index.html
RUN mkdir files

EXPOSE 5000
CMD [ "python3", "extractor_server.py"]