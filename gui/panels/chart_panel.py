#!/usr/bin/env python3
"""
Chart Panel Module
차트 표시 패널 (Time Domain / Spectral)
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.widgets.chart_widget import TimeDomainChart, SpectralChart


class ChartPanel:
    """차트 표시 패널"""

    def __init__(self, parent, chart_type='time_domain', time_window=5):
        """
        Args:
            parent: 부모 위젯
            chart_type: 'time_domain' 또는 'spectral'
            time_window: 시간 윈도우 (분, time_domain만 해당)
        """
        self.parent = parent
        self.chart_type = chart_type
        self.time_window = time_window

        self.frame = tb.LabelFrame(parent, text="📊 Real-time Chart",
                                   padding=10, bootstyle="info")
        self.chart = None

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성"""
        # 툴바 프레임
        toolbar_frame = tb.Frame(self.frame)
        toolbar_frame.pack(fill=X, pady=(0, 5))

        # 차트 생성
        if self.chart_type == 'time_domain':
            self.chart = TimeDomainChart(self.frame, time_window=self.time_window)
        elif self.chart_type == 'spectral':
            self.chart = SpectralChart(self.frame)

        # 캔버스 생성
        canvas_widget = self.chart.create_canvas(toolbar_parent=toolbar_frame)
        canvas_widget.pack(fill=BOTH, expand=True)

    def update_time_domain(self, channel_data, y_limits=None):
        """
        Time Domain 차트 업데이트

        Args:
            channel_data: 채널 데이터 딕셔너리
            y_limits: Y축 제한 (y_min, y_max) 또는 None
        """
        if isinstance(self.chart, TimeDomainChart):
            self.chart.update_data(channel_data, y_limits)

    def update_spectral(self, frequencies, magnitude_db, harmonics=None):
        """
        Spectral Analysis 차트 업데이트

        Args:
            frequencies: 주파수 배열
            magnitude_db: 크기 (dB) 배열
            harmonics: 고조파 리스트
        """
        if isinstance(self.chart, SpectralChart):
            self.chart.update_spectrum(frequencies, magnitude_db, harmonics)

    def enable_cursor(self, enabled):
        """측정 커서 활성화"""
        if self.chart:
            self.chart.enable_cursor(enabled)

    def save_snapshot(self, filename):
        """차트 스냅샷 저장"""
        if self.chart:
            self.chart.save_figure(filename)

    def clear(self):
        """차트 클리어"""
        if self.chart:
            self.chart.clear()

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
