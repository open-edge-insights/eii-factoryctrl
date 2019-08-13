# Dockerfile for FactoryControlApp
ARG EIS_VERSION
FROM ia_pybase:$EIS_VERSION
LABEL description="FactoryControlApp image"
ARG EIS_UID
ARG EIS_USER_NAME
RUN useradd -r -u ${EIS_UID} ${EIS_USER_NAME}

ENV PYTHONPATH ${PYTHONPATH}:.

# Installing dependent python modules
COPY requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

# Adding project depedency modules
ADD factoryctrl_app.py .


RUN mkdir -p logs && \
    chown ${EIS_UID}:${EIS_UID} logs

ENTRYPOINT [ "python3.6", "factoryctrl_app.py" ]
HEALTHCHECK NONE
