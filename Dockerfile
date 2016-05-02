FROM centos:7.2.1511

RUN groupadd -g 427 visualiser && useradd -m -g visualiser -u 427 visualiser

RUN yum install -y epel-release

RUN yum install -y gcc make git python python-devel gdal-devel gdal-python gdal atlas-devel blas-devel \
    lapack-devel proj proj-devel proj-epsg proj-nad geos geos-devel ogr_fdw94 gcc-c++ libpng \
    libpng-devel freetype-devel giflib giflib-devel libxml2 libxml2-devel cairo cairo-devel \
    libjpeg-turbo-devel ibjpeg-turbo libcurl-devel python-pip openssl libffi libffi-devel cmake \
    swig harfbuzz harfbuzz-devel fribidi-devel fribidi fcgi fcgi-devel openssl-devel mailcap

RUN pip install --no-cache numpy==1.10.1 scipy==0.14.0 requests[security]==2.8.1
COPY requirements.txt /tmp/requirements.txt
RUN CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install --upgrade --no-cache -r /tmp/requirements.txt && \
    pip install -f https://github.com/BCCVL/org.bccvl.movelib/archive/1.2.0.tar.gz#egg=org.bccvl.movelib-1.2.0 org.bccvl.movelib[http,swift]==1.2.0


RUN cd /tmp && curl http://download.osgeo.org/mapserver/mapserver-7.0.1.tar.gz | tar xz \
    && cd mapserver-7.0.1 && mkdir build && cd build \
    && cmake -DWITH_CLIENT_WMS=1 -DWITH_CLIENT_WFS=1 -DWITH_CURL=1 -DWITH_PYTHON=1 \
    -DWITH_KML=1 -DWITH_POSTGIS=0 -DCMAKE_INSTALL_PREFIX=/usr .. \
    && make && make install && cd /tmp && rm -rf mapserver-7.0.1

COPY BCCVL_Visualiser/ /opt/visualiser/

RUN cd /opt/visualiser && python setup.py install

RUN pip install --no-cache gunicorn==19.4.1

ENV LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib

ENV BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH /var/opt/visualiser/bccvl/map_data_files
ENV BCCVL_DATA_MOVER_PUBLIC_DIR /var/opt/visualiser/visualiser/visualiser_public

ENV AUTHTKT_SECRET secret

ENV NWORKERS 4
ENV NTHREADS 2

EXPOSE 10600 9191

RUN mkdir /var/opt/visualiser && chown -R visualiser:visualiser /var/opt/visualiser
COPY cmd.sh /cmd.sh
RUN chmod a+x /cmd.sh

RUN mkdir -p /var/opt/visualiser/bccvl/map_data_files && \
    chown -R visualiser:visualiser /var/opt/visualiser/bccvl

CMD ["/cmd.sh"]
