# Dockerfile for FactoryControlApp
ARG IEI_VERSION
FROM ia_pybase:$IEI_VERSION
LABEL description="FactoryControlApp image"

ENV PYTHONPATH ${PYTHONPATH}:./DataAgent/da_grpc/protobuff/py:./DataAgent/da_grpc/protobuff/py/pb_internal
ARG IEI_UID
# Creating dir for streamsublib cert files
RUN mkdir -p /etc/ssl/streamsublib && \
    mkdir -p /etc/ssl/ca && \
    chown -R ${IEI_UID} /etc/ssl/

# Installing dependent python modules
COPY Util/ ./Util/
COPY FactoryControlApp/requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

# Creating dir for ca_certificate

# Adding project depedency modules
COPY FactoryControlApp/ .
COPY StreamSubLib/StreamSubLib.py StreamSubLib/StreamSubLib.py
COPY DataAgent/da_grpc ./DataAgent/da_grpc

ENTRYPOINT [ "python3.6", "FactoryControlApp.py", "--config", "config.json", "--log-dir", "/IEI/factoryctrl_app_logs"]
CMD ["--log", "DEBUG"]
HEALTHCHECK NONE
