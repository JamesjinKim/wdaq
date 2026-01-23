#!/usr/bin/env python3
"""
Status Bar Module
하단 상태바 패널
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
import uuid


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

    def _get_mac_address(self):
        """라즈베리파이의 MAC 주소 가져오기"""
        try:
            # eth0의 MAC 주소 가져오기
            mac = uuid.getnode()
            mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            return mac_address
        except:
            return "N/A"

    def _copy_mac_to_clipboard(self, event):
        """MAC 주소를 클립보드에 복사"""
        try:
            # 클립보드에 MAC 주소 복사
            self.frame.clipboard_clear()
            self.frame.clipboard_append(self.mac_address)
            self.frame.update()  # 클립보드 업데이트

            # 상태 메시지 표시 (일시적으로)
            original_text = self.mac_label.cget("text")
            self.mac_label.config(text=f"Mac Address: {self.mac_address} (Copied!)")

            # 1초 후 원래 텍스트로 복원
            self.frame.after(1000, lambda: self.mac_label.config(text=original_text))

        except Exception as e:
            print(f"Failed to copy MAC address: {e}")

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

        # MAC 주소 표시 (클릭 가능)
        self.mac_address = self._get_mac_address()
        self.mac_label = tb.Label(
            self.frame,
            text=f"Mac Address: {self.mac_address}",
            font=("DejaVu Sans", 9),
            cursor="hand2",  # 마우스 커서를 손 모양으로 변경
            bootstyle="info"  # 클릭 가능함을 시각적으로 표시
        )
        self.mac_label.pack(side=LEFT, padx=20)

        # MAC 주소 클릭 이벤트 바인딩
        self.mac_label.bind("<Button-1>", self._copy_mac_to_clipboard)

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
