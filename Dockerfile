FROM python:2.7-stretch
MAINTAINER info@vizzuality.com

ENV NAME gladAnalysis
ENV USER gladanalysis

RUN apt-get -y update && apt-get -y upgrade && \
   apt-get install -y bash git openssl \
   libffi-dev gcc musl-dev wget libgeos-3.5.1

RUN addgroup $USER && adduser --shell /bin/bash --disabled-login --ingroup $USER $USER

RUN easy_install pip && pip install --upgrade pip
RUN pip install virtualenv gunicorn gevent

RUN mkdir -p /opt/$NAME
COPY requirements.txt /opt/$NAME/requirements.txt
COPY requirements_dev.txt /opt/$NAME/requirements_dev.txt
RUN cd /opt/$NAME && pip install -r requirements.txt
RUN cd /opt/$NAME && pip install -r requirements_dev.txt

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
RUN wget http://gfw2-data.s3.amazonaws.com/forest_change/umd_landsat_alerts/prod/db/stats.db -O /opt/$NAME/data/stats.db

COPY ./microservice /opt/$NAME/microservice
RUN chown -R $USER:$USER /opt/$NAME

# Tell Docker we are going to use this ports
EXPOSE 5702
USER $USER

# Launch script
ENTRYPOINT ["./entrypoint.sh"]
