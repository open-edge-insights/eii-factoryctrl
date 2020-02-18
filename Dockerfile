# Dockerfile for FactoryControlApp
ARG EIS_VERSION
FROM ia_eisbase:$EIS_VERSION as eisbase
LABEL description="FactoryControlApp image"
ARG EIS_UID
ARG EIS_USER_NAME
RUN useradd -r -u ${EIS_UID} ${EIS_USER_NAME}

ENV PYTHONPATH ${PYTHONPATH}:.

# Installing dependent python modules
COPY requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

FROM ia_common:$EIS_VERSION as common

FROM eisbase

COPY --from=common ${GO_WORK_DIR}/common/libs ${PY_WORK_DIR}/libs
COPY --from=common ${GO_WORK_DIR}/common/util ${PY_WORK_DIR}/util
COPY --from=common ${GO_WORK_DIR}/common/cmake ./common/cmake
COPY --from=common /usr/local/lib /usr/local/lib
COPY --from=common /usr/local/lib/python3.6/dist-packages/ /usr/local/lib/python3.6/dist-packages/

# Adding project depedency modules
COPY factoryctrl_app.py .
COPY schema.json .

ENTRYPOINT [ "python3.6", "factoryctrl_app.py" ]
