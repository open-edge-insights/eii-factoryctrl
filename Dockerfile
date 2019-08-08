# Dockerfile for FactoryControlApp
ARG IEI_VERSION
FROM ia_pybase:$IEI_VERSION
LABEL description="FactoryControlApp image"
ARG IEI_UID
ARG IEI_USER_NAME
RUN useradd -r -u ${IEI_UID} ${IEI_USER_NAME}

ENV PYTHONPATH ${PYTHONPATH}:.

# Installing dependent python modules
COPY FactoryControlApp/requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

# Adding project depedency modules
COPY FactoryControlApp/ .
COPY libs/ ./libs

RUN mkdir -p logs && \
    chown ${IEI_UID}:${IEI_UID} logs

ENTRYPOINT [ "python3.6", "factoryctrl_app.py" ]
HEALTHCHECK NONE
