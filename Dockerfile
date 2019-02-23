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

# download pre-calculated tile database
# and check afterwards every five minutes if there is a new file
RUN wget -N http://gfw2-data.s3.amazonaws.com/forest_change/umd_landsat_alerts/prod/db/stats.db -O /opt/$NAME/data/stats.db
RUN echo '*/5  *  *  *  *    wget -N http://gfw2-data.s3.amazonaws.com/forest_change/umd_landsat_alerts/prod/db/stats.db -O /opt/$NAME/data/stats.db' > /etc/crontabs/root

COPY ./microservice /opt/$NAME/microservice
RUN chown -R $USER:$USER /opt/$NAME/data/*

# Tell Docker we are going to use this ports
EXPOSE 5702
USER $USER

# Launch script
ENTRYPOINT ["./entrypoint.sh"]
