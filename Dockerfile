#
# hotmaps/toolbox-backend image Dockerfile
#
#

FROM ubuntu:16.04

MAINTAINER Daniel Hunacek <daniel.hunacek@hevs.ch>

# setup volume
RUN mkdir -p /data
VOLUME /data


# Build commands
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y

# Install required software
RUN apt-get install -y \
	software-properties-common \
    wget

# Install Python 3.6 (and other required software)
RUN add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update && apt-get install -y \
	#libreadline-gplv2-dev \
	#libncursesw5-dev \
	#libssl-dev \
	#libsqlite3-dev \
	#tk-dev \
	#libgdbm-dev \
	#libc6-dev \
	#libbz2-dev \
	#libgeos-dev \
	python3.6 \
	python3.6-dev \
	python3.6-venv \
	python-numpy-dev

# add gdal path for further pip install gdal
#ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
#ENV C_INCLUDE_PATH=/usr/include/gdal

# Install GRASS / pyqgis
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN sh -c 'echo "deb http://qgis.org/ubuntugis xenial main" >> /etc/apt/sources.list'
RUN sh -c 'echo "deb-src http://qgis.org/ubuntugis xenial main " >> /etc/apt/sources.list'
RUN wget -O - http://qgis.org/downloads/qgis-2016.gpg.key | gpg --import
RUN gpg --fingerprint 073D307A618E5811
RUN gpg --export --armor 073D307A618E5811 | apt-key add -
RUN apt-get update && apt-get install -y qgis python-qgis gdal-bin libgdal-dev libgdal1i

# Install pip for Python 3.6
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3

# Install numpy package before requirements.txt as it is required by other packages and must be installed before
RUN pip install numpy

# Make Python3.6 default
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python

# Setup app server
RUN mkdir -p /data
COPY gunicorn-config.py /data/gunicorn-config.py
RUN pip3 install gunicorn

# Install required python modules
COPY requirements.txt /data/requirements.txt
RUN pip3 install -r /data/requirements.txt

# Copy app source app
COPY app /data

WORKDIR /data

EXPOSE 80

# Start server
CMD ["gunicorn", "--config", "/data/gunicorn-config.py", "--log-config", "/data/logging.conf", "wsgi:application"]