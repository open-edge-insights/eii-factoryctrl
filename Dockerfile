# Dockerfile for FactoryControlApp
ARG IEI_VERSION
FROM ia_pybase:$IEI_VERSION
LABEL description="FactoryControlApp image"

# Installing dependent python modules
ADD FactoryControlApp/requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

# Creating dir for ca_certificate
RUN mkdir -p /etc/ssl/ca

# Adding project depedency modules
ADD FactoryControlApp/ .
ADD StreamSubLib/StreamSubLib.py StreamSubLib/StreamSubLib.py
ADD Util/ Util/
ADD DataAgent/da_grpc ./DataAgent/da_grpc

# Creating dir for streamsublib cert files
RUN mkdir -p /etc/ssl/streamsublib

ENV PYTHONPATH ${PYTHONPATH}:./DataAgent/da_grpc/protobuff/py:./DataAgent/da_grpc/protobuff/py/pb_internal
ARG IEI_UID
RUN chown -R ${IEI_UID} /etc/ssl/
ENTRYPOINT [ "python3.6", "FactoryControlApp.py", "--config", "config.json", "--log-dir", "/IEI/factoryctrl_app_logs"]
CMD ["--log", "DEBUG"]
HEALTHCHECK NONE
