#!/usr/bin/env python3
"""
Header Panel Module
상단 헤더 패널 (제목, 연결 상태, 제어 버튼)
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class HeaderPanel:
    """상단 헤더 패널"""

    def __init__(self, parent, callbacks):
        """
        Args:
            parent: 부모 위젯
            callbacks: {
                'on_start_stop': 측정 시작/정지 콜백,
                'on_save_config': 설정 저장 콜백,
                'on_load_config': 설정 불러오기 콜백,
                'on_save_data': 데이터 저장 콜백,
                'on_interval_change': 측정 주기 변경 콜백
            }
        """
        self.parent = parent
        self.callbacks = callbacks

        self.frame = tb.Frame(parent)
        self.interval_var = tk.StringVar(value="1.0")

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성"""
        # 제목
        title_label = tb.Label(
            self.frame,
            text="🔌 ADS8668 8-Channel ADC Monitor",
            font=("DejaVu Sans", 18, "bold"),
            bootstyle="info"
        )
        title_label.pack(side=LEFT)

        # 버튼 영역
        button_frame = tb.Frame(self.frame)
        button_frame.pack(side=RIGHT)

        # 측정 주기 설정
        interval_frame = tb.Frame(button_frame)
        interval_frame.pack(side=RIGHT, padx=10)

        tb.Label(interval_frame, text="Interval:", font=("DejaVu Sans", 9)).pack(side=LEFT, padx=(0, 5))
        tb.Spinbox(
            interval_frame, from_=0.1, to=10.0, increment=0.1,
            textvariable=self.interval_var, width=6,
            command=self._on_interval_change, font=("DejaVu Sans", 9)
        ).pack(side=LEFT)
        tb.Label(interval_frame, text="sec", font=("DejaVu Sans", 9)).pack(side=LEFT, padx=(2, 0))

        # 버튼들
        tb.Button(button_frame, text="💾 Save Data",
                 command=self._on_save_data,
                 bootstyle="secondary", width=10).pack(side=RIGHT, padx=5)

        tb.Button(button_frame, text="📂 Load",
                 command=self._on_load_config,
                 bootstyle="secondary", width=8).pack(side=RIGHT, padx=5)

        tb.Button(button_frame, text="💿 Save Config",
                 command=self._on_save_config,
                 bootstyle="secondary", width=10).pack(side=RIGHT, padx=5)

        self.start_button = tb.Button(
            button_frame, text="▶️ Start",
            command=self._on_start_stop,
            bootstyle="success", width=10
        )
        self.start_button.pack(side=RIGHT, padx=5)

        self.connection_status = tb.Label(
            button_frame, text="⚫ Disconnected",
            font=("DejaVu Sans", 10), bootstyle="danger"
        )
        self.connection_status.pack(side=RIGHT, padx=10)

    def _on_start_stop(self):
        """시작/정지 버튼 콜백"""
        if self.callbacks.get('on_start_stop'):
            self.callbacks['on_start_stop']()

    def _on_save_config(self):
        """설정 저장 콜백"""
        if self.callbacks.get('on_save_config'):
            self.callbacks['on_save_config']()

    def _on_load_config(self):
        """설정 불러오기 콜백"""
        if self.callbacks.get('on_load_config'):
            self.callbacks['on_load_config']()

    def _on_save_data(self):
        """데이터 저장 콜백"""
        if self.callbacks.get('on_save_data'):
            self.callbacks['on_save_data']()

    def _on_interval_change(self):
        """측정 주기 변경 콜백"""
        if self.callbacks.get('on_interval_change'):
            self.callbacks['on_interval_change'](float(self.interval_var.get()))

    def set_connection_status(self, connected):
        """연결 상태 업데이트"""
        if connected:
            self.connection_status.config(text="🟢 Connected", bootstyle="success")
        else:
            self.connection_status.config(text="🔴 Disconnected", bootstyle="danger")

    def set_monitoring_state(self, is_monitoring):
        """모니터링 상태 업데이트"""
        if is_monitoring:
            self.start_button.config(text="⏸️ Stop", bootstyle="warning")
        else:
            self.start_button.config(text="▶️ Start", bootstyle="success")

    def get_interval(self):
        """현재 측정 주기 반환"""
        return float(self.interval_var.get())

    def set_interval(self, interval):
        """측정 주기 설정"""
        self.interval_var.set(f"{interval:.1f}")

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
