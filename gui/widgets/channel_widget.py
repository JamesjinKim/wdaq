#!/usr/bin/env python3
"""
Channel Widget Module
개별 채널 UI 위젯
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class ChannelWidget:
    """개별 채널 제어 위젯"""

    def __init__(self, parent, channel, ranges, on_enable_callback, on_range_callback):
        """
        Args:
            parent: 부모 위젯
            channel: 채널 번호 (0-7)
            ranges: 레인지 정보 딕셔너리
            on_enable_callback: 채널 활성화 콜백 함수(channel, enabled)
            on_range_callback: 레인지 변경 콜백 함수(channel, range_name)
        """
        self.channel = channel
        self.ranges = ranges
        self.on_enable_callback = on_enable_callback
        self.on_range_callback = on_range_callback

        # 위젯 생성
        self.frame = tb.LabelFrame(parent, text=f"CH{channel}", padding=8, bootstyle="primary")

        self._create_widgets()

    def _create_widgets(self):
        """위젯 구성"""
        # 상단: Enable 토글 + 레인지 선택
        top_frame = tb.Frame(self.frame)
        top_frame.pack(fill=X, pady=(0, 5))

        self.enable_var = tk.BooleanVar(value=False)
        tb.Checkbutton(
            top_frame, text="ON", variable=self.enable_var,
            command=self._on_enable_toggle,
            bootstyle="success-round-toggle"
        ).pack(side=LEFT)

        self.range_var = tk.StringVar(value="±10V")
        self.range_combo = tb.Combobox(
            top_frame, textvariable=self.range_var,
            values=[info["name"] for info in self.ranges.values()],
            state="readonly", width=8, font=("DejaVu Sans", 8)
        )
        self.range_combo.pack(side=RIGHT)
        self.range_combo.bind("<<ComboboxSelected>>", self._on_range_change)

        # 중앙: 전압 표시
        voltage_frame = tb.Frame(self.frame)
        voltage_frame.pack(fill=X, pady=5)

        self.voltage_label = tb.Label(
            voltage_frame, text="--", font=("DejaVu Sans", 18, "bold"),
            bootstyle="info", anchor="center"
        )
        self.voltage_label.pack(expand=True)

        tb.Label(voltage_frame, text="Volts", font=("DejaVu Sans", 8), anchor="center").pack()

        # 하단: 프로그레스바
        self.progress = tb.Progressbar(self.frame, mode='determinate',
                                       bootstyle="info-striped", length=150)
        self.progress.pack(fill=X, pady=5)

    def _on_enable_toggle(self):
        """채널 활성화 토글"""
        if self.on_enable_callback:
            self.on_enable_callback(self.channel, self.enable_var.get())

    def _on_range_change(self, event=None):
        """레인지 변경"""
        if self.on_range_callback:
            self.on_range_callback(self.channel, self.range_var.get())

    def update_voltage(self, voltage, progress_pct):
        """
        전압 표시 업데이트

        Args:
            voltage: 전압 값
            progress_pct: 프로그레스바 퍼센트 (0-100)
        """
        self.voltage_label.config(text=f"{voltage:+.4f}")
        self.progress['value'] = max(0, min(100, progress_pct))

    def get_enabled(self):
        """활성화 상태 반환"""
        return self.enable_var.get()

    def set_enabled(self, enabled):
        """활성화 상태 설정"""
        self.enable_var.set(enabled)

    def get_range(self):
        """현재 레인지 반환"""
        return self.range_var.get()

    def set_range(self, range_name):
        """레인지 설정"""
        self.range_var.set(range_name)

    def grid(self, **kwargs):
        """그리드 배치"""
        self.frame.grid(**kwargs)

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
