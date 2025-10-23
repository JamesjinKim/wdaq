#!/usr/bin/env python3
"""
Control Panel Module
차트 컨트롤 및 통계 패널 (탭 방식)
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from gui.widgets.gpio_widget import GPIOStatusWidget, GPIOOutputWidget, GPIOAlarmWidget


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
                'on_channel_display_toggle': 채널 표시 토글 콜백,
                'on_gpio_output_toggle': GPIO 출력 토글 콜백
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

        # GPIO 위젯들
        self.gpio_input_widgets = {}
        self.gpio_output_widgets = {}
        self.gpio_alarm_widget = None

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 (탭 방식)"""
        # 탭 위젯 생성
        self.notebook = tb.Notebook(self.frame)
        self.notebook.pack(fill=BOTH, expand=True)

        # Statistics 탭
        self.stats_tab = tb.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Statistics")
        self._create_statistics_tab()

        # GPIO 탭
        self.gpio_tab = tb.Frame(self.notebook)
        self.notebook.add(self.gpio_tab, text="GPIO")
        self._create_gpio_tab()

    def _create_statistics_tab(self):
        """Statistics 탭 내용 생성"""
        # Y-Scale 설정
        self._create_yscale_section(self.stats_tab)

        # 차트 도구
        self._create_tools_section(self.stats_tab)

        # 채널 표시 선택
        self._create_channel_display_section(self.stats_tab)

        # 통계 정보
        self._create_statistics_section(self.stats_tab)

    def _create_yscale_section(self, parent):
        """Y-Scale 설정 섹션"""
        scale_frame = tb.LabelFrame(parent, text="Y-Scale Control",
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

    def _create_tools_section(self, parent):
        """차트 도구 섹션"""
        tools_frame = tb.LabelFrame(parent, text="Chart Tools",
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

    def _create_channel_display_section(self, parent):
        """채널 표시 선택 섹션"""
        channel_frame = tb.LabelFrame(parent, text="Channel Display",
                                      padding=10, bootstyle="success")
        channel_frame.pack(fill=X, pady=(0, 10))

        for ch in range(8):
            var = tk.BooleanVar(value=False)
            self.chart_channel_vars[ch] = var

            tb.Checkbutton(
                channel_frame, text=f"CH{ch}", variable=var,
                command=lambda c=ch: self._on_channel_display_toggle(c),
                bootstyle="success-round-toggle"
            ).pack(anchor=W, pady=2)

    def _create_statistics_section(self, parent):
        """통계 정보 섹션"""
        stats_frame = tb.LabelFrame(parent, text="Statistics",
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

    def _create_gpio_tab(self):
        """GPIO 탭 내용 생성"""
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(self.gpio_tab, highlightthickness=0)
        scrollbar = tb.Scrollbar(self.gpio_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # 입력 핀 섹션
        input_frame = tb.LabelFrame(scrollable_frame, text="Input Pins",
                                    padding=10, bootstyle="info")
        input_frame.pack(fill=X, pady=(0, 10))

        # GPIO 모니터의 입력 핀 목록 (하드코딩 - 나중에 GPIOMonitor에서 가져올 수 있음)
        input_pins = [
            (13, "DIN (Alarm)"),
            (5, "GPIO 5"),
            (17, "GPIO 17"),
            (22, "GPIO 22"),
            (27, "GPIO 27")
        ]

        for pin, name in input_pins:
            widget = GPIOStatusWidget(input_frame, pin, name)
            widget.pack(fill=X, pady=2)
            self.gpio_input_widgets[pin] = widget

        # 출력 핀 섹션
        output_frame = tb.LabelFrame(scrollable_frame, text="Output Pins",
                                     padding=10, bootstyle="success")
        output_frame.pack(fill=X, pady=(0, 10))

        # CS 핀 (읽기 전용)
        cs_widget = GPIOStatusWidget(output_frame, 8, "CS (SPI)")
        cs_widget.pack(fill=X, pady=2)
        self.gpio_input_widgets[8] = cs_widget  # CS는 상태만 표시

        # DOUT 핀 (제어 가능)
        dout_widget = GPIOOutputWidget(
            output_frame, 12, "DOUT",
            on_toggle=self._on_gpio_output_toggle
        )
        dout_widget.pack(fill=X, pady=2)
        self.gpio_output_widgets[12] = dout_widget

        # ADC 알람 섹션
        alarm_frame = tb.LabelFrame(scrollable_frame, text="ADC Alarm",
                                    padding=10, bootstyle="warning")
        alarm_frame.pack(fill=X, pady=(0, 10))

        self.gpio_alarm_widget = GPIOAlarmWidget(alarm_frame)
        self.gpio_alarm_widget.pack(fill=X)

        # 이벤트 카운터 리셋 버튼
        reset_frame = tb.Frame(scrollable_frame)
        reset_frame.pack(fill=X, pady=(10, 0))

        tb.Button(
            reset_frame,
            text="Reset Event Counters",
            command=self._on_reset_gpio_counters,
            bootstyle="secondary",
            width=20
        ).pack(fill=X, padx=5)

    def _on_gpio_output_toggle(self, pin, state):
        """GPIO 출력 토글 콜백"""
        if self.callbacks.get('on_gpio_output_toggle'):
            return self.callbacks['on_gpio_output_toggle'](pin, state)
        return False

    def _on_reset_gpio_counters(self):
        """GPIO 이벤트 카운터 리셋"""
        if self.callbacks.get('on_reset_gpio_counters'):
            self.callbacks['on_reset_gpio_counters']()

    def update_gpio_input(self, pin, state, event_count=0, last_event_time=0):
        """
        GPIO 입력 상태 업데이트

        Args:
            pin: GPIO 핀 번호
            state: True=HIGH, False=LOW
            event_count: 이벤트 총 횟수
            last_event_time: 마지막 이벤트 시각
        """
        if pin in self.gpio_input_widgets:
            self.gpio_input_widgets[pin].update_state(state, event_count, last_event_time)

    def update_gpio_alarm(self, active=False, channel=None, last_time=0, total_count=0):
        """
        ADC 알람 상태 업데이트

        Args:
            active: 현재 알람 활성 여부
            channel: 트리거된 채널
            last_time: 마지막 알람 시각
            total_count: 총 알람 횟수
        """
        if self.gpio_alarm_widget:
            self.gpio_alarm_widget.update_alarm(active, channel, last_time, total_count)

    def pack(self, **kwargs):
        """팩 배치"""
        self.frame.pack(**kwargs)
