#!/usr/bin/env python3
"""
Channel Panel Module
채널 설정 패널 (8채널 위젯 관리)
"""

import tkinter as tk
import ttkbootstrap as tb
from gui.widgets.channel_widget import ChannelWidget


class ChannelPanel:
    """채널 설정 패널 (2열 x 4행 레이아웃)"""

    def __init__(self, parent, ranges, on_enable_callback, on_range_callback):
        """
        Args:
            parent: 부모 위젯
            ranges: 레인지 정보 딕셔너리
            on_enable_callback: 채널 활성화 콜백 함수(channel, enabled)
            on_range_callback: 레인지 변경 콜백 함수(channel, range_name)
        """
        self.parent = parent
        self.ranges = ranges
        self.on_enable_callback = on_enable_callback
        self.on_range_callback = on_range_callback

        self.frame = tb.Frame(parent)
        self.channel_widgets = {}

        self._create_widgets()

    def _create_widgets(self):
        """8개 채널 위젯 생성 (2열 레이아웃)"""
        for row in range(4):
            for col in range(2):
                ch = row * 2 + col
                widget = ChannelWidget(
                    self.frame, ch, self.ranges,
                    self.on_enable_callback,
                    self.on_range_callback
                )
                widget.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                self.channel_widgets[ch] = widget

                # 그리드 크기 균등 배분
                self.frame.grid_rowconfigure(row, weight=1)
                self.frame.grid_columnconfigure(col, weight=1)

    def update_channel_display(self, channel, voltage, progress_pct):
        """
        채널 표시 업데이트

        Args:
            channel: 채널 번호
            voltage: 전압 값
            progress_pct: 프로그레스바 퍼센트
        """
        if channel in self.channel_widgets:
            self.channel_widgets[channel].update_voltage(voltage, progress_pct)

    def get_channel_enabled(self, channel):
        """채널 활성화 상태 반환"""
        if channel in self.channel_widgets:
            return self.channel_widgets[channel].get_enabled()
        return False

    def set_channel_enabled(self, channel, enabled):
        """채널 활성화 상태 설정"""
        if channel in self.channel_widgets:
            self.channel_widgets[channel].set_enabled(enabled)

    def get_channel_range(self, channel):
        """채널 레인지 반환"""
        if channel in self.channel_widgets:
            return self.channel_widgets[channel].get_range()
        return None

    def set_channel_range(self, channel, range_name):
        """채널 레인지 설정"""
        if channel in self.channel_widgets:
            self.channel_widgets[channel].set_range(range_name)

    def get_all_states(self):
        """모든 채널 상태 반환"""
        states = {}
        for ch in range(8):
            states[ch] = {
                'enabled': self.get_channel_enabled(ch),
                'range': self.get_channel_range(ch)
            }
        return states

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
