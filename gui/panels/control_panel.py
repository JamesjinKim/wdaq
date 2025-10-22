#!/usr/bin/env python3
"""
Control Panel Module
차트 컨트롤 및 통계 패널
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class ControlPanel:
    """차트 컨트롤 및 통계 패널"""

    Y_SCALE_PRESETS = {
        "Auto mode": None,
        "±10V Full": (-10.5, 10.5),
        "±5V Full": (-5.5, 5.5),
        "±2.5V Full": (-2.75, 2.75),
        "0-10V Full": (-0.5, 10.5),
        "0-5V Full": (-0.5, 5.5),
        "Custom": "custom"
    }

    def __init__(self, parent, callbacks):
        """
        Args:
            parent: 부모 위젯
            callbacks: {
                'on_scale_change': Y-Scale 모드 변경 콜백,
                'on_apply_custom_scale': 커스텀 스케일 적용 콜백,
                'on_cursor_toggle': 커서 토글 콜백,
                'on_save_snapshot': 스냅샷 저장 콜백,
                'on_channel_display_toggle': 채널 표시 토글 콜백
            }
        """
        self.parent = parent
        self.callbacks = callbacks

        self.frame = tb.Frame(parent)
        self.y_scale_var = tk.StringVar(value="Auto mode")
        self.y_min_var = tk.StringVar(value="-12.0000")
        self.y_max_var = tk.StringVar(value="+12.0000")
        self.cursor_var = tk.BooleanVar(value=False)
        self.chart_channel_vars = {}
        self.stats_labels = {}

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성"""
        # Y-Scale 설정
        self._create_yscale_section()

        # 차트 도구
        self._create_tools_section()

        # 채널 표시 선택
        self._create_channel_display_section()

        # 통계 정보
        self._create_statistics_section()

    def _create_yscale_section(self):
        """Y-Scale 설정 섹션"""
        scale_frame = tb.LabelFrame(self.frame, text="Y-Scale Control",
                                    padding=10, bootstyle="primary")
        scale_frame.pack(fill=X, pady=(0, 10))

        tb.Label(scale_frame, text="Mode:", font=("DejaVu Sans", 9)).pack(anchor=W)
        scale_combo = tb.Combobox(
            scale_frame, textvariable=self.y_scale_var,
            values=list(self.Y_SCALE_PRESETS.keys()),
            state="readonly", width=15
        )
        scale_combo.pack(fill=X, pady=5)
        scale_combo.bind("<<ComboboxSelected>>", lambda e: self._on_scale_change())

        tb.Label(scale_frame, text="Y-Min:", font=("DejaVu Sans", 9)).pack(anchor=W, pady=(5, 0))
        self.y_min_entry = tb.Entry(scale_frame, textvariable=self.y_min_var,
                                    width=15, state="disabled", bootstyle="info")
        self.y_min_entry.pack(fill=X)
        # Enter 키로도 적용 가능하도록
        self.y_min_entry.bind('<Return>', lambda e: self._on_apply_custom_scale())

        tb.Label(scale_frame, text="Y-Max:", font=("DejaVu Sans", 9)).pack(anchor=W, pady=(5, 0))
        self.y_max_entry = tb.Entry(scale_frame, textvariable=self.y_max_var,
                                    width=15, state="disabled", bootstyle="info")
        self.y_max_entry.pack(fill=X)
        # Enter 키로도 적용 가능하도록
        self.y_max_entry.bind('<Return>', lambda e: self._on_apply_custom_scale())

        self.apply_scale_btn = tb.Button(
            scale_frame, text="Apply", command=self._on_apply_custom_scale,
            bootstyle="success", state="disabled"
        )
        self.apply_scale_btn.pack(fill=X, pady=(5, 0))

    def _create_tools_section(self):
        """차트 도구 섹션"""
        tools_frame = tb.LabelFrame(self.frame, text="Chart Tools",
                                    padding=10, bootstyle="secondary")
        tools_frame.pack(fill=X, pady=(0, 10))

        tb.Checkbutton(
            tools_frame, text="Enable Cursor", variable=self.cursor_var,
            command=self._on_cursor_toggle, bootstyle="info-round-toggle"
        ).pack(anchor=W, pady=2)

        tb.Button(
            tools_frame, text="Save Snapshot", command=self._on_save_snapshot,
            bootstyle="info", width=18
        ).pack(fill=X, pady=2)

    def _create_channel_display_section(self):
        """채널 표시 선택 섹션"""
        channel_frame = tb.LabelFrame(self.frame, text="Channel Display",
                                      padding=10, bootstyle="success")
        channel_frame.pack(fill=X, pady=(0, 10))

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
                 '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']

        for ch in range(8):
            var = tk.BooleanVar(value=False)
            self.chart_channel_vars[ch] = var

            ch_frame = tb.Frame(channel_frame)
            ch_frame.pack(fill=X, pady=1)

            tb.Checkbutton(
                ch_frame, text=f"CH{ch}", variable=var,
                command=lambda c=ch: self._on_channel_display_toggle(c),
                bootstyle="success-toolbutton"
            ).pack(side=LEFT)

            # 색상 인디케이터
            color_label = tk.Label(ch_frame, text="█", fg=colors[ch],
                                  font=("DejaVu Sans", 12))
            color_label.pack(side=RIGHT)

    def _create_statistics_section(self):
        """통계 정보 섹션"""
        stats_frame = tb.LabelFrame(self.frame, text="Statistics",
                                    padding=10, bootstyle="warning")
        stats_frame.pack(fill=BOTH, expand=True)

        # 채널 선택
        tb.Label(stats_frame, text="Channel:", font=("DejaVu Sans", 9, "bold")).pack(anchor=W)
        self.stats_channel_var = tk.StringVar(value="CH0")
        stats_ch_combo = tb.Combobox(
            stats_frame, textvariable=self.stats_channel_var,
            values=[f"CH{i}" for i in range(8)],
            state="readonly", width=12
        )
        stats_ch_combo.pack(fill=X, pady=(0, 10))

        # 통계 값들
        stats_items = [
            ("RMS:", "rms"),
            ("Max:", "max"),
            ("Min:", "min"),
            ("Avg:", "avg"),
            ("P-P:", "pp")
        ]

        for label_text, key in stats_items:
            frame = tb.Frame(stats_frame)
            frame.pack(fill=X, pady=2)
            tb.Label(frame, text=label_text, font=("DejaVu Sans", 9, "bold"),
                    width=5, anchor=W).pack(side=LEFT)
            label = tb.Label(frame, text="--", font=("DejaVu Sans", 10),
                           bootstyle="info")
            label.pack(side=RIGHT)
            self.stats_labels[key] = label

    def _on_scale_change(self):
        """Y-Scale 모드 변경"""
        mode = self.y_scale_var.get()

        if mode == "Auto mode":
            self.y_min_entry.config(state="disabled")
            self.y_max_entry.config(state="disabled")
            self.apply_scale_btn.config(state="disabled")
        elif mode == "Custom":
            # Custom 모드: 사용자가 자유롭게 입력 가능
            self.y_min_entry.config(state="normal")
            self.y_max_entry.config(state="normal")
            self.apply_scale_btn.config(state="normal")
        else:
            # 프리셋 모드: 프리셋 값을 표시하되, 수동 수정 가능하도록 변경
            preset = self.Y_SCALE_PRESETS[mode]
            if preset:
                self.y_min_var.set(f"{preset[0]:.4f}")
                self.y_max_var.set(f"{preset[1]:.4f}")

            # 프리셋 값을 기반으로 수정 가능하도록 활성화
            self.y_min_entry.config(state="normal")
            self.y_max_entry.config(state="normal")
            self.apply_scale_btn.config(state="normal")

        if self.callbacks.get('on_scale_change'):
            self.callbacks['on_scale_change'](mode)

    def _on_apply_custom_scale(self):
        """커스텀 스케일 적용"""
        if self.callbacks.get('on_apply_custom_scale'):
            try:
                y_min = float(self.y_min_var.get())
                y_max = float(self.y_max_var.get())

                # 유효성 검사
                if y_min >= y_max:
                    # 입력 필드를 빨간색으로 하이라이트
                    self.y_min_entry.config(bootstyle="danger")
                    self.y_max_entry.config(bootstyle="danger")
                    return

                # 유효한 값이면 정상 색상으로 복원
                self.y_min_entry.config(bootstyle="info")
                self.y_max_entry.config(bootstyle="info")

                self.callbacks['on_apply_custom_scale'](y_min, y_max)
            except ValueError:
                # 숫자가 아닌 값 입력 시 빨간색 하이라이트
                self.y_min_entry.config(bootstyle="danger")
                self.y_max_entry.config(bootstyle="danger")

    def _on_cursor_toggle(self):
        """커서 토글"""
        if self.callbacks.get('on_cursor_toggle'):
            self.callbacks['on_cursor_toggle'](self.cursor_var.get())

    def _on_save_snapshot(self):
        """스냅샷 저장"""
        if self.callbacks.get('on_save_snapshot'):
            self.callbacks['on_save_snapshot']()

    def _on_channel_display_toggle(self, channel):
        """채널 표시 토글"""
        if self.callbacks.get('on_channel_display_toggle'):
            self.callbacks['on_channel_display_toggle'](
                channel, self.chart_channel_vars[channel].get()
            )

    def update_statistics(self, stats):
        """
        통계 업데이트

        Args:
            stats: {'rms': ..., 'max': ..., 'min': ..., 'avg': ..., 'pp': ...}
        """
        for key, value in stats.items():
            if key in self.stats_labels:
                if key == 'rms' or key == 'pp':
                    self.stats_labels[key].config(text=f"{value:.4f} V")
                else:
                    self.stats_labels[key].config(text=f"{value:+.4f} V")

    def get_y_scale_limits(self):
        """현재 Y-Scale 제한 반환"""
        mode = self.y_scale_var.get()
        if mode == "Auto mode":
            return None
        elif mode == "Custom":
            try:
                return (float(self.y_min_var.get()), float(self.y_max_var.get()))
            except ValueError:
                return None
        else:
            return self.Y_SCALE_PRESETS[mode]

    def set_channel_display(self, channel, enabled):
        """채널 표시 설정"""
        if channel in self.chart_channel_vars:
            self.chart_channel_vars[channel].set(enabled)

    def get_stats_channel(self):
        """통계 표시 채널 반환"""
        ch_name = self.stats_channel_var.get()
        return int(ch_name.replace("CH", ""))

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
