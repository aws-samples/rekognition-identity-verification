FROM python:3.9

RUN apt-get -y update && apt-get -y install --no-install-recommends npm curl zip \
  && npm install -g aws-cdk

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN curl -sSL https://get.docker.com/ | sh

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ship-it.sh /usr/local/bin/ship-it
RUN chmod a+x /usr/local/bin/ship-it
