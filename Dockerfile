FROM centos:7.2.1511

RUN groupadd -g 1042 bccvl && useradd -m -g bccvl -u 1042 bccvl 

RUN yum install -y epel-release

RUN yum install -y gcc make git python python-devel gdal-devel gdal atlas-devel blas-devel \ 
    lapack-devel proj proj-devel proj-epsg proj-nad geos geos-devel ogr_fdw94 gcc-c++ libpng \
    libpng-devel freetype-devel giflib giflib-devel libxml2 libxml2-devel cairo cairo-devel \
    libjpeg-turbo-devel ibjpeg-turbo libcurl-devel python-pip openssl libffi libffi-devel cmake \
    swig harfbuzz harfbuzz-devel fribidi-devel fribidi fcgi fcgi-devel openssl-devel mailcap

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --no-cache numpy==1.10.1 scipy==0.14.0 requests[security]==2.8.1
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade --no-cache -r /tmp/requirements.txt

RUN cd /tmp && curl http://download.osgeo.org/mapserver/mapserver-7.0.0.tar.gz | tar xz \
    && cd mapserver-7.0.0 && mkdir build && cd build \
    && cmake -DWITH_CLIENT_WMS=1 -DWITH_CLIENT_WFS=1 -DWITH_CURL=1 -DWITH_PYTHON=1 \
    -DWITH_KML=1 -DWITH_POSTGIS=0 -DCMAKE_INSTALL_PREFIX=/usr .. \
    && make && make install && cd /tmp && rm -rf mapserver-7.0.0


RUN mkdir -p /bccvl_visualiser
COPY BCCVL_Visualiser /bccvl_visualiser/BCCVL_Visualiser

RUN cd /bccvl_visualiser/BCCVL_Visualiser && python setup.py install

RUN chown -R bccvl:bccvl /bccvl_visualiser/BCCVL_Visualiser

RUN pip install --no-cache gunicorn==19.4.1

ENV LD_LIBRARY_PATH=/lib:/usr/lib:/usr/local/lib


ENV BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH /bccvltmp/visualiser/bccvl/map_data_files
ENV BCCVL_DATA_MOVER_PUBLIC_DIR /bccvltmp/visualiser/visualiser_public

ENV AUTHTKT_SECRET secret

ENV NWORKERS 4
ENV NTHREADS 2

EXPOSE 10600 9191

RUN mkdir /bccvltmp && chown -R bccvl:bccvl /bccvltmp 
COPY cmd.sh /cmd.sh
RUN chmod a+x /cmd.sh

USER bccvl
RUN mkdir -p /tmp/bccvl/map_data_files

CMD ["/cmd.sh"]


