# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=${INSTALL_PYTHON_VERSION:-PYTHON_VERSION_NOT_SET}

FROM python:${INSTALL_PYTHON_VERSION}-slim-buster AS builder

WORKDIR /app

COPY requirements requirements
RUN pip install --no-cache -r requirements/prod.txt

COPY autoapp.py ./
COPY {{cookiecutter.app_name}} {{cookiecutter.app_name}}
COPY .env.example .env

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

# COPY --from=builder --chown=sid:sid /app/{{ cookiecutter.app_name }}/static /app/{{ cookiecutter.app_name }}/static

COPY requirements requirements
RUN pip install --no-cache --user -r requirements/prod.txt

COPY . .

EXPOSE 5000
ENTRYPOINT ["/bin/bash", "bin/service.sh"]
# CMD ["-c", "/etc/supervisor/supervisord.conf"]


# ================================= DEVELOPMENT ================================
# FROM builder AS development

# RUN pip install --no-cache -r requirements/dev.txt
# EXPOSE 2992
# EXPOSE 5000
