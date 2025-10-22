#!/usr/bin/env python3
"""
Status Bar Module
하단 상태바 패널
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime


class StatusBar:
    """하단 상태바"""

    def __init__(self, parent):
        """
        Args:
            parent: 부모 위젯
        """
        self.parent = parent
        self.frame = tb.Frame(parent)

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성"""
        self.status_text = tb.Label(
            self.frame, text="Ready",
            font=("DejaVu Sans", 9), bootstyle="secondary"
        )
        self.status_text.pack(side=LEFT)

        self.sample_rate_label = tb.Label(
            self.frame,
            text="Sample Rate: 1.00 Hz (1.0s)",
            font=("DejaVu Sans", 9)
        )
        self.sample_rate_label.pack(side=LEFT, padx=20)

        self.time_label = tb.Label(
            self.frame, text="",
            font=("DejaVu Sans", 9)
        )
        self.time_label.pack(side=RIGHT)

    def set_status(self, text):
        """상태 텍스트 설정"""
        self.status_text.config(text=text)

    def set_sample_rate(self, interval):
        """샘플링 레이트 표시 업데이트"""
        sample_rate = 1.0 / interval if interval > 0 else 0
        self.sample_rate_label.config(
            text=f"Sample Rate: {sample_rate:.2f} Hz ({interval:.1f}s)"
        )

    def update_time(self):
        """현재 시간 업데이트"""
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
