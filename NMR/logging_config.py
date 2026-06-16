# -*- coding: utf-8 -*-
"""
日志配置模块 — 配置并返回模块级日志对象。
"""

import logging

from NMR.config import LOGGER_NAME


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """
    配置并返回模块级日志对象。

    Args:
        level: 日志级别。

    Returns:
        logging.Logger: 已配置的日志对象。
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


LOGGER = configure_logging()
"""logging.Logger: 模块级日志对象，其他模块通过 ``from NMR.logging_config import LOGGER`` 引用。"""
