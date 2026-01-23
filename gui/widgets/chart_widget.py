#!/usr/bin/env python3
"""
Chart Widget Module
차트 위젯 (Time Domain / Spectral Analysis)
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.widgets import Cursor
from datetime import datetime, timedelta
import numpy as np


class BaseChartWidget:
    """차트 위젯 베이스 클래스"""

    def __init__(self, parent, figsize=(10, 6), dpi=100):
        self.parent = parent
        self.fig = Figure(figsize=figsize, dpi=dpi, facecolor='#2E3440')
        self.ax = self.fig.add_subplot(111, facecolor='#2E3440')
        self.canvas = None
        self.toolbar = None
        self.cursor = None

        self._setup_style()

    def _setup_style(self):
        """스타일 설정"""
        plt.style.use('dark_background')
        self.ax.tick_params(colors='#D8DEE9', labelsize=9)
        self.ax.grid(True, alpha=0.3, color='#4C566A')

    def create_canvas(self, toolbar_parent=None):
        """캔버스 생성"""
        self.canvas = FigureCanvasTkAgg(self.fig, self.parent)
        self.canvas.draw()

        # 툴바 추가
        if toolbar_parent:
            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_parent)
            self.toolbar.update()

        return self.canvas.get_tk_widget()

    def enable_cursor(self, enabled=True):
        """측정 커서 활성화"""
        if enabled and not self.cursor:
            self.cursor = Cursor(self.ax, useblit=True, color='yellow', linewidth=1)
        elif not enabled and self.cursor:
            self.cursor = None
            self.canvas.draw()

    def save_figure(self, filename, dpi=300):
        """그림 저장"""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight',
                        facecolor='#2E3440', edgecolor='none')

    def clear(self):
        """차트 클리어"""
        self.ax.clear()
        self._setup_style()


class TimeDomainChart(BaseChartWidget):
    """Time Domain 차트 위젯 (ch1.png 참조)"""

    def __init__(self, parent, time_window=5, figsize=(10, 6), dpi=100):
        super().__init__(parent, figsize, dpi)
        self.time_window = time_window  # 분 단위
        self.lines = {}
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
                      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']

        self._setup_time_chart()

    def _setup_time_chart(self):
        """Time Domain 차트 설정"""
        self.ax.set_xlabel('Time', color='#D8DEE9', fontsize=10)
        self.ax.set_ylabel('Voltage (V)', color='#D8DEE9', fontsize=10)

        # 8개 채널 라인 생성
        for ch in range(8):
            line, = self.ax.plot([], [], '-', color=self.colors[ch],
                               label=f'CH{ch}', linewidth=2, alpha=0.8)
            self.lines[ch] = line

        self.ax.legend(loc='upper left', framealpha=0.8, facecolor='#3B4252',
                      fontsize=8, ncol=4)

        # 시간 축 초기화
        now = datetime.now()
        self.ax.set_xlim(now - timedelta(minutes=self.time_window), now)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def update_data(self, channel_data, y_limits=None):
        """
        차트 데이터 업데이트

        Args:
            channel_data: {ch: {'timestamps': [...], 'voltages': [...], 'enabled': bool}, ...}
            y_limits: (y_min, y_max) 튜플 또는 None (Auto)
        """
        has_data = False

        for ch in range(8):
            if ch in channel_data and channel_data[ch]['enabled'] and len(channel_data[ch]['timestamps']) > 0:
                self.lines[ch].set_data(
                    channel_data[ch]['timestamps'],
                    channel_data[ch]['voltages']
                )
                self.lines[ch].set_visible(True)
                has_data = True
            else:
                self.lines[ch].set_visible(False)

        if has_data:
            # X축 업데이트
            now = datetime.now()
            self.ax.set_xlim(now - timedelta(minutes=self.time_window), now)

            # Y축 업데이트
            if y_limits is None:
                # Auto mode
                all_v = []
                for ch in range(8):
                    if ch in channel_data and channel_data[ch]['enabled']:
                        all_v.extend(channel_data[ch]['voltages'])

                if all_v:
                    v_min, v_max = min(all_v), max(all_v)
                    margin = (v_max - v_min) * 0.1 if v_max != v_min else 1
                    self.ax.set_ylim(v_min - margin, v_max + margin)
            else:
                self.ax.set_ylim(y_limits[0], y_limits[1])

            self.canvas.draw()


class SpectralChart(BaseChartWidget):
    """Spectral Analysis 차트 위젯 (ch2.png 참조)"""

    def __init__(self, parent, figsize=(10, 6), dpi=100):
        super().__init__(parent, figsize, dpi)
        self.spectrum_line = None
        self.harmonic_markers = []

        self._setup_spectral_chart()

    def _setup_spectral_chart(self):
        """Spectral Analysis 차트 설정"""
        self.ax.set_xlabel('Frequency (Hz)', color='#D8DEE9', fontsize=10)
        self.ax.set_ylabel('Amplitude (dBC)', color='#D8DEE9', fontsize=10)

        # 스펙트럼 라인
        self.spectrum_line, = self.ax.plot([], [], '-', color='#4ECDC4',
                                          linewidth=1.5, alpha=0.8)

    def update_spectrum(self, frequencies, magnitude_db, harmonics=None, mark_dc=True):
        """
        스펙트럼 업데이트

        Args:
            frequencies: 주파수 배열
            magnitude_db: 크기 (dB) 배열
            harmonics: [(order, freq, mag), ...] 고조파 리스트
            mark_dc: DC 성분 표시 여부
        """
        if frequencies is None or magnitude_db is None:
            return

        # 스펙트럼 그리기
        self.spectrum_line.set_data(frequencies, magnitude_db)

        # 고조파 마커 제거
        for marker in self.harmonic_markers:
            marker.remove()
        self.harmonic_markers = []

        # 고조파 마커 추가
        if harmonics:
            for order, freq, mag in harmonics:
                marker = self.ax.plot(freq, 20 * np.log10(mag) if mag > 0 else -120,
                                    'ro', markersize=6)[0]
                self.harmonic_markers.append(marker)

                # 레이블 추가
                text = self.ax.text(freq, 20 * np.log10(mag) if mag > 0 else -120,
                                   f'  [H{order}]', color='white', fontsize=8)
                self.harmonic_markers.append(text)

        # 축 범위 자동 조정
        self.ax.set_xlim(0, max(frequencies))
        self.ax.set_ylim(np.min(magnitude_db) - 10, np.max(magnitude_db) + 10)

        self.canvas.draw()

    def clear_spectrum(self):
        """스펙트럼 클리어"""
        self.spectrum_line.set_data([], [])
        for marker in self.harmonic_markers:
            marker.remove()
        self.harmonic_markers = []
        self.canvas.draw()
