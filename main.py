#!/usr/bin/env python3
"""
ADS8668 ADC Monitor - Main Entry Point
모듈화된 8채널 ADC 모니터 프로그램
"""

import sys
import logging
from tkinter import messagebox

# 한글 폰트 설정 (matplotlib)
import matplotlib.pyplot as plt
try:
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
except:
    plt.rcParams['font.family'] = 'sans-serif'

from utils.logger import setup_logger
from gui.main_window import MainWindow


def main():
    """메인 함수"""
    # 로거 설정
    logger = setup_logger(name='ads8668_monitor', level=logging.INFO)
    logger.info("ADS8668 Monitor Starting...")

    try:
        # 메인 윈도우 실행
        app = MainWindow()
        app.run()

    except Exception as e:
        logger.error(f"Program error: {e}", exc_info=True)
        messagebox.showerror("Error", f"Failed to start:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
