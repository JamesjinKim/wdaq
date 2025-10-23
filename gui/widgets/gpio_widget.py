#!/usr/bin/env python3
"""
GPIO Widget Module
GPIO 상태 표시 위젯
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import time


class GPIOStatusWidget(tb.Frame):
    """GPIO 입력 핀 상태 표시 위젯"""

    def __init__(self, parent, pin, pin_name):
        """
        GPIO 상태 위젯 초기화

        Args:
            parent: 부모 위젯
            pin: GPIO 핀 번호
            pin_name: 핀 이름
        """
        super().__init__(parent)
        self.pin = pin
        self.pin_name = pin_name

        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        # 전체 프레임
        container = tb.Frame(self)
        container.pack(fill=X, pady=2)

        # 좌측: 핀 이름
        name_label = tb.Label(
            container,
            text=self.pin_name,
            width=12,
            anchor=W,
            font=("Helvetica", 9)
        )
        name_label.pack(side=LEFT, padx=(5, 10))

        # 중앙: 상태 표시 (원형 인디케이터)
        self.state_indicator = tb.Label(
            container,
            text="[O]",
            width=3,
            font=("Courier", 10, "bold"),
            foreground="gray"
        )
        self.state_indicator.pack(side=LEFT, padx=5)

        # 상태 텍스트
        self.state_label = tb.Label(
            container,
            text="LOW",
            width=5,
            anchor=W,
            font=("Helvetica", 9)
        )
        self.state_label.pack(side=LEFT, padx=5)

        # 우측: 이벤트 카운트
        self.event_label = tb.Label(
            container,
            text="Events: 0",
            width=12,
            anchor=E,
            font=("Helvetica", 8),
            foreground="gray"
        )
        self.event_label.pack(side=RIGHT, padx=5)

    def update_state(self, state, event_count=0, last_event_time=0):
        """
        상태 업데이트

        Args:
            state: True=HIGH, False=LOW
            event_count: 이벤트 총 횟수
            last_event_time: 마지막 이벤트 시각 (time.time() 형식)
        """
        if state:
            # HIGH 상태
            self.state_indicator.config(text="[#]", foreground="lime")
            self.state_label.config(text="HIGH", foreground="lime")
        else:
            # LOW 상태
            self.state_indicator.config(text="[O]", foreground="gray")
            self.state_label.config(text="LOW", foreground="lightgray")

        # 이벤트 카운트 표시
        if event_count > 0:
            # 마지막 이벤트로부터 경과 시간 계산
            if last_event_time > 0:
                elapsed = time.time() - last_event_time
                if elapsed < 60:
                    time_str = f"{elapsed:.1f}s ago"
                elif elapsed < 3600:
                    time_str = f"{elapsed/60:.1f}m ago"
                else:
                    time_str = f"{elapsed/3600:.1f}h ago"

                self.event_label.config(
                    text=f"Events: {event_count} ({time_str})",
                    foreground="lightblue"
                )
            else:
                self.event_label.config(
                    text=f"Events: {event_count}",
                    foreground="lightblue"
                )
        else:
            self.event_label.config(text="Events: 0", foreground="gray")


class GPIOOutputWidget(tb.Frame):
    """GPIO 출력 핀 제어 위젯"""

    def __init__(self, parent, pin, pin_name, on_toggle=None):
        """
        GPIO 출력 위젯 초기화

        Args:
            parent: 부모 위젯
            pin: GPIO 핀 번호
            pin_name: 핀 이름
            on_toggle: 토글 콜백 함수 (pin, state)
        """
        super().__init__(parent)
        self.pin = pin
        self.pin_name = pin_name
        self.on_toggle = on_toggle
        self.current_state = False

        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        container = tb.Frame(self)
        container.pack(fill=X, pady=2)

        # 좌측: 핀 이름
        name_label = tb.Label(
            container,
            text=self.pin_name,
            width=12,
            anchor=W,
            font=("Helvetica", 9)
        )
        name_label.pack(side=LEFT, padx=(5, 10))

        # 중앙: 상태 표시
        self.state_indicator = tb.Label(
            container,
            text="[O]",
            width=3,
            font=("Courier", 10, "bold"),
            foreground="gray"
        )
        self.state_indicator.pack(side=LEFT, padx=5)

        # 상태 텍스트
        self.state_label = tb.Label(
            container,
            text="LOW",
            width=5,
            anchor=W,
            font=("Helvetica", 9)
        )
        self.state_label.pack(side=LEFT, padx=5)

        # 우측: 토글 버튼
        self.toggle_btn = tb.Button(
            container,
            text="Set HIGH",
            width=10,
            command=self.toggle_output,
            bootstyle="success-outline"
        )
        self.toggle_btn.pack(side=RIGHT, padx=5)

    def toggle_output(self):
        """출력 토글"""
        new_state = not self.current_state

        if self.on_toggle:
            # 콜백 실행
            success = self.on_toggle(self.pin, new_state)
            if success:
                self.set_state(new_state)
        else:
            self.set_state(new_state)

    def set_state(self, state):
        """
        상태 설정

        Args:
            state: True=HIGH, False=LOW
        """
        self.current_state = state

        if state:
            # HIGH 상태
            self.state_indicator.config(text="[#]", foreground="lime")
            self.state_label.config(text="HIGH", foreground="lime")
            self.toggle_btn.config(text="Set LOW", bootstyle="warning-outline")
        else:
            # LOW 상태
            self.state_indicator.config(text="[O]", foreground="gray")
            self.state_label.config(text="LOW", foreground="lightgray")
            self.toggle_btn.config(text="Set HIGH", bootstyle="success-outline")


class GPIOAlarmWidget(tb.Frame):
    """ADC 알람 상태 표시 위젯"""

    def __init__(self, parent):
        """
        알람 위젯 초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """UI 구성"""
        # 타이틀
        title_label = tb.Label(
            self,
            text="ADC Alarm Status",
            font=("Helvetica", 10, "bold")
        )
        title_label.pack(anchor=W, padx=5, pady=(5, 2))

        # 상태 프레임
        status_frame = tb.Frame(self)
        status_frame.pack(fill=X, padx=5, pady=5)

        # 알람 상태
        tb.Label(status_frame, text="Status:", width=8, anchor=W).pack(side=LEFT)
        self.status_label = tb.Label(
            status_frame,
            text="Inactive",
            font=("Helvetica", 9, "bold"),
            foreground="gray"
        )
        self.status_label.pack(side=LEFT, padx=5)

        # 트리거 채널
        trigger_frame = tb.Frame(self)
        trigger_frame.pack(fill=X, padx=5, pady=2)

        tb.Label(trigger_frame, text="Channel:", width=8, anchor=W).pack(side=LEFT)
        self.channel_label = tb.Label(
            trigger_frame,
            text="None",
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.channel_label.pack(side=LEFT, padx=5)

        # 마지막 알람 시각
        time_frame = tb.Frame(self)
        time_frame.pack(fill=X, padx=5, pady=2)

        tb.Label(time_frame, text="Last:", width=8, anchor=W).pack(side=LEFT)
        self.time_label = tb.Label(
            time_frame,
            text="Never",
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.time_label.pack(side=LEFT, padx=5)

        # 총 알람 횟수
        count_frame = tb.Frame(self)
        count_frame.pack(fill=X, padx=5, pady=2)

        tb.Label(count_frame, text="Total:", width=8, anchor=W).pack(side=LEFT)
        self.count_label = tb.Label(
            count_frame,
            text="0",
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.count_label.pack(side=LEFT, padx=5)

    def update_alarm(self, active=False, channel=None, last_time=0, total_count=0):
        """
        알람 상태 업데이트

        Args:
            active: 현재 알람 활성 여부
            channel: 트리거된 채널 번호 (None이면 없음)
            last_time: 마지막 알람 시각 (time.time() 형식)
            total_count: 총 알람 횟수
        """
        if active:
            self.status_label.config(text="Active", foreground="red")
        else:
            self.status_label.config(text="Inactive", foreground="gray")

        if channel is not None:
            self.channel_label.config(
                text=f"CH{channel}",
                foreground="orange" if active else "gray"
            )
        else:
            self.channel_label.config(text="None", foreground="gray")

        if last_time > 0:
            elapsed = time.time() - last_time
            if elapsed < 60:
                time_str = f"{elapsed:.1f}s ago"
            elif elapsed < 3600:
                time_str = f"{elapsed/60:.1f}m ago"
            else:
                time_str = f"{elapsed/3600:.1f}h ago"
            self.time_label.config(text=time_str, foreground="lightblue")
        else:
            self.time_label.config(text="Never", foreground="gray")

        self.count_label.config(
            text=str(total_count),
            foreground="lightblue" if total_count > 0 else "gray"
        )
