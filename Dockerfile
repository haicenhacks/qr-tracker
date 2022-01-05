FROM python:3.7-alpine3.9
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt /
RUN pip3 install -r /requirements.txt


ADD ./app /app
WORKDIR /app
#ENTRYPOINT ["./entrypoint.sh"]
CMD gunicorn --chdir app main:app -w 2 --threads 2 -b 0.0.0.0:5002

#CMD gunicorn --bind 0.0.0.0:5001 app:main
#CMD python app.py
