FROM node:16

RUN apt-get -y update && apt-get -y install --no-install-recommends python3-pip npm curl zip groff \
  && npm install -g aws-cdk@2.1.0

RUN /usr/bin/python3 -m pip install --upgrade pip
RUN curl -sSL https://get.docker.com/ | sh

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ship-it.sh /usr/local/bin/ship-it
RUN chmod a+x /usr/local/bin/ship-it
