#!/usr/bin/env python3
"""
ADS8668 ADC Monitor - Main Entry Point
모듈화된 8채널 ADC 모니터 프로그램
"""

import sys
import logging

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
    # 루트 로거 설정 (모든 모듈의 로그 출력)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    logger = logging.getLogger(__name__)
    logger.info("="*60)
    logger.info("ADS8668 Monitor Starting...")
    logger.info("="*60)

    try:
        # 메인 윈도우 실행
        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Program error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
