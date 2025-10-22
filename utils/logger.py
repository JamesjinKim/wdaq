#!/usr/bin/env python3
"""
Logger Configuration Module
로깅 설정
"""

import logging
import sys
from datetime import datetime


def setup_logger(name=None, level=logging.INFO, log_file=None):
    """
    로거 설정

    Args:
        name: 로거 이름 (None이면 root logger)
        level: 로그 레벨
        log_file: 로그 파일 경로 (None이면 콘솔만)

    Returns:
        설정된 logger 객체
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 기존 핸들러 제거
    logger.handlers.clear()

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (옵션)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name):
    """로거 가져오기"""
    return logging.getLogger(name)
