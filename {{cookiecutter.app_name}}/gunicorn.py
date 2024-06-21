# -*- coding: utf-8 -*-
"""The gunicorn config module."""

import os

LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.expanduser("~"), "logs", "{{cookiecutter.app_name}}"))
os.makedirs(LOG_DIR, exist_ok=True)

from dotenv import find_dotenv, load_dotenv  # !!! 解决 celery 无法加载环境变量的问题

load_dotenv(find_dotenv())

class GunicornConfig(object):
    workers = 2
    threads = 2
    workers = 2
    # 指定每个工作者的线程数
    threads = 2
    # 监听内网端口5000
    bind = "0.0.0.0:{}".format(os.getenv("BIND_PORT", 5000))
    # 设置守护进程,将进程交给supervisor管理
    daemon = "false"
    # 工作模式协程
    worker_class = "gevent"
    # 设置最大并发量
    worker_connections = 2000
    # 设置进程文件目录
    pidfile = os.path.join(LOG_DIR, "gunicorn.pid")
    loglevel = "DEBUG"

    timeout = 30
    keepalive = 60

    debug = False
    logconfig_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        # 在最新版本必须添加root配置，否则抛出Error: Unable to configure root logger
        # "root": {
        #       "level": "DEBUG",
        #       "handlers": ["console"] # 对应handlers字典的键（key）
        # },
        "loggers": {
            "gunicorn.error": {
                "level": "DEBUG",  # 打日志的等级；
                "handlers": ["error_file", "console"],  # 对应handlers字典的键（key）；
                # 是否将日志打印到控制台（console），若为True（或1），将打印在supervisor日志监控文件logfile上，对于测试非常好用；
                "propagate": 0,
                "qualname": "gunicorn_error",
            },
            "gunicorn.access": {
                "level": "DEBUG",
                "handlers": ["access_file", "console"],
                "propagate": 0,
                "qualname": "access",
            },
        },
        "handlers": {
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1024 * 1024 * 100,  # 打日志的大小（此处限制100mb）
                "backupCount": 10,  # 备份数量（若需限制日志大小，必须存在值，且为最小正整数）
                "formatter": "generic",  # 对应formatters字典的键（key）
                "filename": f"{LOG_DIR}/gunicorn.log",  # 若对配置无特别需求，仅需修改此路径
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "maxBytes": 1024 * 1024 * 100,
                "backupCount": 1,
                "formatter": "access",
                "filename": f"{LOG_DIR}/access.log",  # 若对配置无特别需求，仅需修改此路径
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "generic",
            },
        },
        "formatters": {
            "generic": {
                "format": "%(asctime)s | %(process)d | %(levelname)s | %(filename)s:%(funcName)s:[line:%(lineno)d] - %(message)s",  # 打日志的格式
                # "datefmt": "[%Y-%m-%d %H:%M:%S %z]",  # 时间显示格式
                "class": "logging.Formatter",
            },
            "access": {
                "format": "%(message)s",  # 打日志的格式
                # "datefmt": "%Y-%m-%d %H:%M:%S %z",  # 时间显示格式
                "class": "logging.Formatter",
            },
        },
    }


GUNICORN_CONFIG = GunicornConfig


# # 并行工作进程数
workers = GUNICORN_CONFIG.workers or 2
# # 指定每个工作者的线程数
threads = GUNICORN_CONFIG.threads or 2
# # 监听内网端口5000
bind = GUNICORN_CONFIG.bind or "0.0.0.0:8080"
# # 设置守护进程,将进程交给supervisor管理
daemon = GUNICORN_CONFIG.daemon or False
# # 工作模式协程
worker_class = GUNICORN_CONFIG.worker_class or "gevent"
# # 设置最大并发量
worker_connections = GUNICORN_CONFIG.worker_connections or 2000
# # 设置进程文件目录
pidfile = GUNICORN_CONFIG.pidfile or "/tmp/gunicorn.pid"

# # 设置日志记录水平
loglevel = GUNICORN_CONFIG.loglevel or "DEBUG"

timeout = GUNICORN_CONFIG.timeout or 30
keepalive = GUNICORN_CONFIG.keepalive or 60

debug = GUNICORN_CONFIG.debug or True

if GUNICORN_CONFIG.logconfig_dict:
    logconfig_dict = GUNICORN_CONFIG.logconfig_dict
else:
    # 设置访问日志和错误信息日志路径
    accesslog = "/tmp/access.log"
    errorlog = "/tmp/gunicorn_error.log"
