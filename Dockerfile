FROM python:2.7-alpine
MAINTAINER Sergio Gordillo sergio.gordillo@vizzuality.com

ENV NAME gladAnalysis
ENV USER gladAnalysis

RUN apk update && apk upgrade && \
   apk add --no-cache --update bash git openssl-dev build-base alpine-sdk \
   libffi-dev gcc python2-dev musl-dev

# add GEOS for shapely
RUN echo "http://mirror.leaseweb.com/alpine/edge/testing/" >> /etc/apk/repositories
RUN apk add --no-cache geos-dev

RUN addgroup $USER && adduser -s /bin/bash -D -G $USER $USER

RUN easy_install pip && pip install --upgrade pip
RUN pip install virtualenv gunicorn gevent

RUN mkdir -p /opt/$NAME
RUN cd /opt/$NAME && virtualenv venv && source venv/bin/activate
COPY requirements.txt /opt/$NAME/requirements.txt
RUN cd /opt/$NAME && pip install -r requirements.txt

COPY entrypoint.sh /opt/$NAME/entrypoint.sh
COPY main.py /opt/$NAME/main.py
COPY test.py /opt/$NAME/test.py
COPY gunicorn.py /opt/$NAME/gunicorn.py

# Copy the application folder inside the container
WORKDIR /opt/$NAME
COPY ./$NAME /opt/$NAME/$NAME

# create data directory and download MVT export databases
RUN mkdir -p /opt/$NAME/data

# download all pre-calculated tile databases
RUN wget http://s3.amazonaws.com/palm-risk-poc/data/mvt/africa.mbtiles -O /opt/$NAME/data/africa.mbtiles
RUN wget http://s3.amazonaws.com/palm-risk-poc/data/mvt/south_america.mbtiles -O /opt/$NAME/data/south_america.mbtiles
RUN wget http://s3.amazonaws.com/palm-risk-poc/data/mvt/asia.mbtiles -O /opt/$NAME/data/asia.mbtiles

COPY ./microservice /opt/$NAME/microservice
RUN chown $USER:$USER /opt/$NAME
RUN chown $USER:$USER /opt/$NAME/data/
RUN chown $USER:$USER /opt/$NAME/data/africa.mbtiles
RUN chown $USER:$USER /opt/$NAME/data/asia.mbtiles
RUN chown $USER:$USER /opt/$NAME/data/south_america.mbtiles

# Tell Docker we are going to use this ports
EXPOSE 5702
USER $USER

# Launch script
ENTRYPOINT ["./entrypoint.sh"]
