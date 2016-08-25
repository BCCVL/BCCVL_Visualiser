FROM hub.bccvl.org.au/bccvl/visualiserbase:2016-08-25

RUN groupadd -g 427 visualiser && \
    useradd -m -g visualiser -u 427 visualiser

COPY BCCVL_Visualiser/ /opt/visualiser/

RUN cd /opt/visualiser && \
    CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install --upgrade --no-cache -r /opt/visualiser/requirements.txt && \
    python setup.py develop

ENV BCCVL_MAPSCRIPT_MAP_DATA_FILES_ROOT_PATH /var/opt/visualiser/bccvl/map_data_files
ENV BCCVL_DATA_MOVER_PUBLIC_DIR /var/opt/visualiser/visualiser/visualiser_public

ENV AUTHTKT_SECRET secret

ENV NWORKERS 4
ENV NTHREADS 2

EXPOSE 10600 9191

RUN mkdir -p /var/opt/visualiser/bccvl/map_data_files && \
    chown -R visualiser:visualiser /var/opt/visualiser

COPY cmd.sh /cmd.sh

CMD ["/cmd.sh"]
