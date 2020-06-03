# Copyright (c) 2020 Intel Corporation.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Dockerfile for FactoryControlApp

ARG EIS_VERSION
ARG DOCKER_REGISTRY
FROM ${DOCKER_REGISTRY}ia_eisbase:$EIS_VERSION as eisbase
LABEL description="FactoryControlApp image"
ARG EIS_UID
ARG EIS_USER_NAME
RUN useradd -r -u ${EIS_UID} ${EIS_USER_NAME}

ENV PYTHONPATH ${PYTHONPATH}:.

# Installing dependent python modules
COPY requirements.txt .
RUN pip3.6 install -r requirements.txt && \
    rm -rf requirements.txt

FROM ${DOCKER_REGISTRY}ia_common:$EIS_VERSION as common

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
