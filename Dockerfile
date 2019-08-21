# Dockerfile for FactoryControlApp
ARG EIS_VERSION
FROM ia_pybase:$EIS_VERSION as pybase
LABEL description="FactoryControlApp image"
ARG EIS_UID
ARG EIS_USER_NAME
RUN useradd -r -u ${EIS_UID} ${EIS_USER_NAME}

ENV PYTHONPATH ${PYTHONPATH}:.

# Installing dependent python modules
COPY requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

RUN mkdir -p logs && \
    chown ${EIS_UID}:${EIS_UID} logs

FROM ia_common:$EIS_VERSION as common

FROM pybase

COPY --from=common /libs ${PY_WORK_DIR}/libs
COPY --from=common /Util ${PY_WORK_DIR}/Util

RUN cd ./libs/EISMessageBus && \
    rm -rf build deps && \
    mkdir build && \
    cd build && \
    cmake -DWITH_PYTHON=ON .. && \
    make && \
    make install

ENV LD_LIBRARY_PATH /usr/local/lib

# Adding project depedency modules
ADD factoryctrl_app.py .

ENTRYPOINT [ "python3.6", "factoryctrl_app.py" ]
HEALTHCHECK NONE
