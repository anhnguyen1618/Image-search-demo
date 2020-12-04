FROM tensorflow/tensorflow 
WORKDIR /usr/app
COPY ./extractors/requirements.txt ./ 

RUN pip install -r requirements.txt

COPY ./extractors/extractor_server.py extractor_server.py
COPY ./extractors/extractors.py extractors.py
COPY ./extractors/templates/index.html ./templates/index.html
RUN mkdir tmp 

EXPOSE 5000
CMD [ "python3", "extractor_server.py"]