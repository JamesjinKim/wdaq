"""
Digital I/O Panel
디지털 입출력 제어 및 모니터링 패널
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import logging

logger = logging.getLogger(__name__)


class DigitalIOPanel(ttk.Frame):
    """디지털 입출력 제어 패널"""

    def __init__(self, parent, callbacks=None):
        """
        Digital I/O 패널 초기화

        Args:
            parent: 부모 위젯
            callbacks: 콜백 함수 딕셔너리
                - on_output_toggle: (pin, state) -> None
                - on_start_monitoring: () -> None
                - on_stop_monitoring: () -> None
        """
        super().__init__(parent, padding=10)
        self.callbacks = callbacks or {}

        # 상태 변수
        self.output_states = {23: False, 24: False}
        self.input_state = False
        self.monitoring_active = False
        self.event_log = []  # 최근 이벤트 로그 (최대 10개)

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성"""
        # 제목
        title = ttk.Label(
            self,
            text="Digital I/O Control",
            font=("Arial", 12, "bold")
        )
        title.pack(fill=X, pady=(0, 10))

        # 디지털 출력 섹션
        self._create_output_section()

        # 구분선
        separator1 = ttk.Separator(self, orient=HORIZONTAL)
        separator1.pack(fill=X, pady=10)

        # 디지털 입력 섹션
        self._create_input_section()

        # 구분선
        separator2 = ttk.Separator(self, orient=HORIZONTAL)
        separator2.pack(fill=X, pady=10)

        # 이벤트 로그 섹션
        self._create_event_log_section()

    def _create_output_section(self):
        """디지털 출력 섹션 생성"""
        # 출력 프레임
        output_frame = ttkb.Labelframe(self, text="Digital Output", padding=10)
        output_frame.pack(fill=BOTH, expand=False)

        # GPIO 23 제어
        self._create_output_control(output_frame, 23, row=0)

        # GPIO 24 제어
        self._create_output_control(output_frame, 24, row=1)

    def _create_output_control(self, parent, pin, row):
        """
        개별 출력 핀 제어 위젯 생성

        Args:
            parent: 부모 위젯
            pin: GPIO 핀 번호
            row: 그리드 행 번호
        """
        # 핀 번호 레이블
        pin_label = ttk.Label(parent, text=f"GPIO {pin}:", width=10)
        pin_label.grid(row=row, column=0, sticky=W, padx=5, pady=5)

        # LOW 버튼
        low_btn = ttkb.Button(
            parent,
            text="LOW",
            bootstyle=SECONDARY,
            width=8,
            command=lambda: self._toggle_output(pin, False)
        )
        low_btn.grid(row=row, column=1, padx=5, pady=5)

        # HIGH 버튼
        high_btn = ttkb.Button(
            parent,
            text="HIGH",
            bootstyle=SUCCESS,
            width=8,
            command=lambda: self._toggle_output(pin, True)
        )
        high_btn.grid(row=row, column=2, padx=5, pady=5)

        # 상태 표시 레이블
        state_label = ttk.Label(parent, text="State:", width=6)
        state_label.grid(row=row, column=3, sticky=W, padx=5, pady=5)

        state_value = ttk.Label(
            parent,
            text="LOW",
            width=8,
            foreground="gray"
        )
        state_value.grid(row=row, column=4, sticky=W, padx=5, pady=5)

        # 위젯 참조 저장
        setattr(self, f"state_label_{pin}", state_value)
        setattr(self, f"low_btn_{pin}", low_btn)
        setattr(self, f"high_btn_{pin}", high_btn)

    def _create_input_section(self):
        """디지털 입력 섹션 생성"""
        # 입력 프레임
        input_frame = ttkb.Labelframe(self, text="Digital Input", padding=10)
        input_frame.pack(fill=BOTH, expand=False)

        # GPIO 13 상태
        pin_label = ttk.Label(input_frame, text="GPIO 13:", width=10)
        pin_label.grid(row=0, column=0, sticky=W, padx=5, pady=5)

        state_label = ttk.Label(input_frame, text="State:", width=6)
        state_label.grid(row=0, column=1, sticky=W, padx=5, pady=5)

        self.input_state_label = ttk.Label(
            input_frame,
            text="LOW",
            width=8,
            foreground="gray"
        )
        self.input_state_label.grid(row=0, column=2, sticky=W, padx=5, pady=5)

        # 모니터링 제어 버튼
        self.monitor_btn = ttkb.Button(
            input_frame,
            text="Start Monitoring",
            bootstyle=PRIMARY,
            command=self._toggle_monitoring
        )
        self.monitor_btn.grid(row=1, column=0, columnspan=3, padx=5, pady=10)

    def _create_event_log_section(self):
        """이벤트 로그 섹션 생성"""
        # 로그 프레임
        log_frame = ttkb.Labelframe(self, text="Event Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True)

        # 스크롤바와 텍스트 위젯
        scroll_frame = ttk.Frame(log_frame)
        scroll_frame.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log_text = tk.Text(
            scroll_frame,
            height=8,
            width=40,
            yscrollcommand=scrollbar.set,
            state=DISABLED,
            font=("Courier", 9)
        )
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # 로그 클리어 버튼
        clear_btn = ttkb.Button(
            log_frame,
            text="Clear Log",
            bootstyle=SECONDARY,
            command=self._clear_log
        )
        clear_btn.pack(pady=5)

    def _toggle_output(self, pin, state):
        """
        출력 핀 상태 토글

        Args:
            pin: GPIO 핀 번호
            state: True(HIGH) 또는 False(LOW)
        """
        logger.info(f"GPIO {pin} 출력 요청: {'HIGH' if state else 'LOW'}")

        # 콜백 호출
        if 'on_output_toggle' in self.callbacks:
            success = self.callbacks['on_output_toggle'](pin, state)
            if success:
                self.update_output_state(pin, state)

    def _toggle_monitoring(self):
        """입력 모니터링 시작/중지"""
        if not self.monitoring_active:
            # 모니터링 시작
            if 'on_start_monitoring' in self.callbacks:
                success = self.callbacks['on_start_monitoring']()
                if success:
                    self.monitoring_active = True
                    self.monitor_btn.config(text="Stop Monitoring")
                    self.monitor_btn.config(bootstyle=DANGER)
                    self._add_log_entry("Monitoring started")
        else:
            # 모니터링 중지
            if 'on_stop_monitoring' in self.callbacks:
                self.callbacks['on_stop_monitoring']()
                self.monitoring_active = False
                self.monitor_btn.config(text="Start Monitoring")
                self.monitor_btn.config(bootstyle=PRIMARY)
                self._add_log_entry("Monitoring stopped")

    def _clear_log(self):
        """이벤트 로그 클리어"""
        self.event_log.clear()
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)

    def _add_log_entry(self, message):
        """
        이벤트 로그에 항목 추가

        Args:
            message: 로그 메시지
        """
        # 최대 100개 항목 유지
        if len(self.event_log) >= 100:
            self.event_log.pop(0)

        self.event_log.append(message)

        # 텍스트 위젯 업데이트
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, message + "\n")
        self.log_text.see(END)  # 자동 스크롤
        self.log_text.config(state=DISABLED)

    def update_output_state(self, pin, state):
        """
        출력 핀 상태 표시 업데이트

        Args:
            pin: GPIO 핀 번호
            state: True(HIGH) 또는 False(LOW)
        """
        self.output_states[pin] = state
        state_label = getattr(self, f"state_label_{pin}", None)

        if state_label:
            state_text = "HIGH" if state else "LOW"
            state_color = "green" if state else "gray"
            state_label.config(text=state_text, foreground=state_color)

    def update_input_state(self, state):
        """
        입력 핀 상태 표시 업데이트

        Args:
            state: True(HIGH) 또는 False(LOW)
        """
        self.input_state = state
        state_text = "HIGH" if state else "LOW"
        state_color = "blue" if state else "gray"
        self.input_state_label.config(text=state_text, foreground=state_color)

    def add_event(self, pin, edge, timestamp):
        """
        GPIO 이벤트 로그 추가

        Args:
            pin: GPIO 핀 번호
            edge: 'rising' 또는 'falling'
            timestamp: 이벤트 발생 시각
        """
        state = "HIGH" if edge == "rising" else "LOW"
        message = f"[{timestamp}] GPIO {pin}: {edge.upper()} -> {state}"
        self._add_log_entry(message)

        # 입력 상태 업데이트
        if pin == 13:
            self.update_input_state(edge == "rising")

    def set_connected(self, connected):
        """
        GPIO 연결 상태에 따른 UI 업데이트

        Args:
            connected: GPIO 연결 여부
        """
        state = NORMAL if connected else DISABLED

        # 출력 버튼 활성화/비활성화
        for pin in [23, 24]:
            low_btn = getattr(self, f"low_btn_{pin}", None)
            high_btn = getattr(self, f"high_btn_{pin}", None)
            if low_btn:
                low_btn.config(state=state)
            if high_btn:
                high_btn.config(state=state)

        # 모니터링 버튼 활성화/비활성화
        self.monitor_btn.config(state=state)

        if not connected:
            self._add_log_entry("GPIO not connected")
