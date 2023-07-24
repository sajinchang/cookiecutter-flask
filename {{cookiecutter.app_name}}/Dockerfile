# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-3.10}
ARG BIND_PORT=${BIND_PORT:-8080}

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app

USER root
ENV PATH="/root/.local/bin:${PATH}"
COPY requirements requirements
RUN apt update -y && apt install -y curl iproute2 procps less
RUN pip install --upgrade pip
RUN pip install --no-cache -r requirements/prod.txt  --no-warn-script-location

COPY . .

EXPOSE ${BIND_PORT}
EXPOSE 5555

ENTRYPOINT ["/bin/bash", "bin/service.sh"]

# docker build -f Dockerfile -t {{cookiecutter.app_name}}:latest . 
