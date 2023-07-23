# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-3.10}
ARG BIND_PORT=${BIND_PORT:-8080}

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY requirements requirements
RUN pip install --no-cache --user -r requirements/prod.txt

COPY . .

EXPOSE ${BIND_PORT}
EXPOSE 5555

ENTRYPOINT ["/bin/bash", "bin/service.sh"]

# docker build -f Dockerfile -t {{cookiecutter.app_name}}:latest . 