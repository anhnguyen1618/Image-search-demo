FROM tensorflow/tensorflow 
WORKDIR /usr/app
COPY ./extract_worker/requirements.txt ./ 

RUN pip install -r requirements.txt

COPY ./extractors/extractors.py extractors.py
COPY ./bucket/bucket.py bucket.py
COPY ./utilities/utilities.py utilities.py
COPY ./extract_worker/extract_worker.py extract_worker.py
COPY ./extract_worker/key.json key.json

ENV GOOGLE_APPLICATION_CREDENTIALS "key.json"

RUN mkdir tmp

CMD [ "python3", "extract_worker.py"]