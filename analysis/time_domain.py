#!/usr/bin/env python3
"""
Time Domain Analysis Module
시간 영역 신호 분석
"""

import numpy as np
from analysis.statistics import SignalStatistics
import logging

logger = logging.getLogger(__name__)


class TimeDomainAnalyzer:
    """시간 영역 신호 분석 클래스"""

    def __init__(self):
        self.stats = SignalStatistics()

    def analyze(self, data):
        """
        시간 영역 분석 수행

        Args:
            data: 시간 영역 신호 데이터

        Returns:
            분석 결과 딕셔너리
        """
        if len(data) == 0:
            return None

        return self.stats.calculate_statistics(data)

    def detect_peaks(self, data, threshold=None):
        """
        피크 검출

        Args:
            data: 신호 데이터
            threshold: 검출 임계값 (None이면 평균 + 1*std)

        Returns:
            피크 인덱스 리스트
        """
        if len(data) < 3:
            return []

        arr = np.array(data)

        if threshold is None:
            threshold = np.mean(arr) + np.std(arr)

        peaks = []
        for i in range(1, len(arr) - 1):
            if arr[i] > arr[i - 1] and arr[i] > arr[i + 1] and arr[i] > threshold:
                peaks.append(i)

        return peaks

    def calculate_frequency(self, data, sample_rate):
        """
        신호 주파수 추정 (zero-crossing 기반)

        Args:
            data: 신호 데이터
            sample_rate: 샘플링 레이트 (Hz)

        Returns:
            추정 주파수 (Hz)
        """
        if len(data) < 10:
            return 0.0

        arr = np.array(data)
        # DC 제거
        arr = arr - np.mean(arr)

        # Zero-crossing 검출
        crossings = 0
        for i in range(1, len(arr)):
            if (arr[i - 1] < 0 and arr[i] >= 0) or (arr[i - 1] >= 0 and arr[i] < 0):
                crossings += 1

        # 주파수 계산 (zero-crossing의 절반)
        duration = len(arr) / sample_rate
        frequency = (crossings / 2) / duration if duration > 0 else 0.0

        return frequency
