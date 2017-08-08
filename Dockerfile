#
# hotmaps/toolbox-backend image Dockerfile
#
#

# docker container prune
# docker image prune
# http://192.168.99.100:9006/api/

FROM ubuntu:16.04

MAINTAINER Daniel Hunacek <daniel.hunacek@hevs.ch>

# setup volume 
RUN mkdir -p /data
VOLUME /data

# Build commands
RUN apt-get update
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y

# Install required softwarerequirements

RUN apt-get install -y \
	software-properties-common \
    wget\
    bzip2

# Install Python 3.6 (and other required software)
#RUN add-apt-repository ppa:jonathonf/python-3.6

#RUN apt-get update && apt-get install -y \
#	#libreadline-gplv2-dev \
#	#libncursesw5-dev \
#	#libssl-dev \
#	#libsqlite3-dev \
#	#tk-dev \
#	#libgdbm-dev \
#	#libc6-dev \
#	#libbz2-dev \
#	#libgeos-dev \
#	python3.6 \
#	python3.6-dev \
#	python3.6-venv \
#	python-numpy-dev
    
#RUN wget https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh
#RUN bash Anaconda3-4.4.0-Linux-x86_64.sh -b

## Make Anaconda/Python3 default
#RUN ln -sf ~/anaconda3/bin/python /usr/local/bin/python
#RUN ln -sf ~/anaconda3/bin/python3 /usr/local/bin/python3
#RUN ln -sf ~/anaconda3/bin/pip /usr/local/bin/pip
#RUN ln -sf ~/anaconda3/bin/pip /usr/local/bin/pip3
#RUN ln -sf ~/anaconda3/bin/conda /usr/local/bin/conda

#ENV PATH=~/anaconda3/bin/:$PATH
#RUN echo $PATH

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN apt-get install -y python3-pip

RUN ln -sf /usr/bin/pip3 /usr/bin/pip

RUN find / -name python
RUN find / -name python3
RUN find / -name pip
RUN find / -name pip3


RUN python --version
RUN python3 --version
RUN pip --version
RUN pip3 --version
#RUN conda --version

# add gdal path for further pip install gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install GRASS / pyqgis
#RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
#RUN sh -c 'echo "deb http://qgis.org/ubuntugis xenial main" >> /etc/apt/sources.list'
#RUN sh -c 'echo "deb-src http://qgis.org/ubuntugis xenial main " >> /etc/apt/sources.list'
#RUN wget -O - http://qgis.org/downloads/qgis-2016.gpg.key | gpg --import
#RUN gpg --fingerprint 073D307A618E5811
#RUN gpg --export --armor 073D307A618E5811 | apt-key add -
#RUN apt-get update && apt-get install -y qgis python-qgis gdal-bin libgdal-dev libgdal1i

# Install pip for Python 3.6
#RUN wget https://bootstrap.pypa.io/get-pip.py
#RUN python3.6 get-pip.py
#RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3

# Install numpy package before requirements.txt as it is required by other packages and must be installed before
#RUN pip install numpy

# Make Python3.6 default
#RUN ln -s /usr/bin/python3.6 /usr/local/bin/python

## Sara: Try to install OSGEO (https://stackoverflow.com/questions/37294127/python-gdal-2-1-installation-on-ubuntu-16-04):
RUN add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN apt-get update
RUN apt-get install -y gdal-bin python-gdal python3-gdal

# Setup app server
RUN mkdir -p /data
COPY gunicorn-config.py /data/gunicorn-config.py
RUN pip3 install gunicorn

# Install required python modules
COPY requirements.txt /data/requirements.txt
RUN pip3 install -r /data/requirements.txt



# Copy app source app
COPY app /data

# TODO: make it beautiful
COPY src/ /data

#RUN find /data

# may be possible...
#RUN touch /data/__init__.py

#RUN cat /data/src/FEAT/F63_bottomup_heat_density_map/F_63.py

#RUN find / -iname gdal\*

WORKDIR /data

EXPOSE 80
RUN echo $PATH
#RUN find / -name gunicorn

# Start server
CMD ["gunicorn", "--config", "/data/gunicorn-config.py", "--log-config", "/data/logging.conf", "wsgi:application"]
