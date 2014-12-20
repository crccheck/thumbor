FROM ubuntu:14.04
# change this to thumbor?
MAINTAINER <c@crccheck.com>


RUN apt-get -qq update

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  # python
  python \
  python-dev \
  python-pip \
  # for pycurl
  libcurl4-openssl-dev \
  # pil/pillow
  libjpeg-dev && \
  DEBIAN_FRONTEND=noninteractive apt-get build-dep python-imaging -y

ADD . /app

WORKDIR /app

RUN python setup.py install

EXPOSE 8888

CMD ["thumbor", "-p", "8888", "-l", "info"]
