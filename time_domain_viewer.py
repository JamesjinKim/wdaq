#!/usr/bin/env python3
"""
Time Domain Viewer
- README.md의 Time Domain Display 부분을 구현한 독립 실행형 GUI
- 기존의 ChartPanel, ControlPanel을 재사용하여 제작
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import time
import queue
from datetime import datetime
import random
import math

# 기존 프로젝트 모듈 임포트
# 경로 문제를 해결하기 위해 sys.path에 현재 경로 추가
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.panels.chart_panel import ChartPanel
from gui.panels.control_panel import ControlPanel
from data.data_manager import DataManager
from analysis.statistics import SignalStatistics

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TimeDomainViewer:
    """Time Domain Display GUI"""

    def __init__(self):
        # 데이터 관리
        self.data_manager = DataManager(max_points=300)
        self.statistics = SignalStatistics()

        # 모니터링 상태
        self.is_monitoring = False
        self.monitor_thread = None
        self.data_queue = queue.Queue()
        self.sample_interval = 0.1  # 시뮬레이션 데이터 업데이트 주기 (초)

        # GUI 초기화
        self.setup_gui()
        self.start_monitoring() # 앱 시작 시 바로 시뮬레이션 시작
        self.start_update_loop()

    def setup_gui(self):
        """GUI 구성"""
        self.root = tb.Window(
            title="Time Domain Viewer",
            themename="darkly",
            size=(1400, 800),
            resizable=(True, True)
        )

        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # 컨트롤 콜백 정의
        control_callbacks = {
            'on_scale_change': self.on_scale_mode_change,
            'on_apply_custom_scale': self.on_apply_custom_scale,
            'on_cursor_toggle': self.on_cursor_toggle,
            'on_save_snapshot': self.save_chart_snapshot,
            'on_channel_display_toggle': self.on_channel_display_toggle,
            # GPIO/Digital I/O 관련 콜백은 필요 없으므로 None 또는 빈 함수 할당
            'on_gpio_output_toggle': lambda p, s: None,
            'on_reset_gpio_counters': lambda: None,
            'on_digital_output_toggle': lambda p, s: None,
            'on_start_digital_monitoring': lambda: None,
            'on_stop_digital_monitoring': lambda: None,
        }

        # 좌측: 컨트롤 패널
        left_frame = tb.Frame(main_frame, width=400)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        self.control_panel = ControlPanel(left_frame, control_callbacks)
        self.control_panel.pack(fill=BOTH, expand=True)
        # 초기 채널 활성화
        for ch in range(8):
            self.on_channel_display_toggle(ch, True)


        # 우측: 차트 패널
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self.chart_panel = ChartPanel(
            right_frame,
            chart_type='time_domain',
            time_window=10 # 10초
        )
        self.chart_panel.pack(fill=BOTH, expand=True)

        # 상태바
        self.status_bar = tb.Frame(self.root, height=30)
        self.status_bar.pack(fill=X, side=BOTTOM, padx=10, pady=(0, 10))
        self.status_label = tb.Label(self.status_bar, text="Viewer initialized. Starting simulation...", bootstyle="info")
        self.status_label.pack(side=LEFT)


    # --- 콜백 메소드 ---
    def on_channel_display_toggle(self, channel, enabled):
        """차트 채널 표시 토글"""
        self.data_manager.enable_channel(channel, enabled)
        self.control_panel.set_channel_display(channel, enabled)
        logging.info(f"Chart display for CH{channel} {'enabled' if enabled else 'disabled'}")

    def on_scale_mode_change(self, mode):
        """Y-Scale 모드 변경"""
        self.status_label.config(text=f"Y-Scale mode changed to: {mode}")
        logging.info(f"Y-Scale mode: {mode}")
        # 차트를 즉시 업데이트하여 스케일 변경 반영
        self.update_chart()

    def on_apply_custom_scale(self, y_min, y_max):
        """커스텀 Y-Scale 적용"""
        if y_min >= y_max:
            messagebox.showwarning("Invalid Input", "Y-Min must be less than Y-Max")
            return
        self.status_label.config(text=f"Applied custom Y-Scale: [{y_min:.2f}, {y_max:.2f}]")
        logging.info(f"Custom Y-Scale applied: [{y_min}, {y_max}]")
        # 차트를 즉시 업데이트하여 스케일 변경 반영
        self.update_chart()

    def on_cursor_toggle(self, enabled):
        """커서 토글"""
        self.chart_panel.enable_cursor(enabled)
        self.status_label.config(text=f"Cursor {'enabled' if enabled else 'disabled'}")
        logging.info(f"Cursor {'enabled' if enabled else 'disabled'}")

    def save_chart_snapshot(self):
        """차트 스냅샷 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"time_domain_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        if not filename:
            return
        try:
            self.chart_panel.save_snapshot(filename)
            self.status_label.config(text=f"Chart saved to {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"Chart snapshot saved successfully!\n\n{filename}")
            logging.info(f"Chart saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chart snapshot:\n{e}")
            logging.error(f"Failed to save chart: {e}")

    # --- 데이터 시뮬레이션 및 GUI 업데이트 ---
    def start_monitoring(self):
        """시뮬레이션 모니터링 시작"""
        self.is_monitoring = True
        self.status_label.config(text="Simulation running...")
        logging.info("Starting data simulation thread.")
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """시뮬레이션 모니터링 중지"""
        self.is_monitoring = False
        self.status_label.config(text="Simulation stopped.")
        logging.info("Stopping data simulation.")

    def monitor_loop(self):
        """시뮬레이션 데이터 생성 루프 (별도 스레드)"""
        sample_count = 0
        while self.is_monitoring:
            try:
                results = {}
                for ch in range(8):
                    if self.data_manager.is_channel_enabled(ch):
                        t = sample_count * self.sample_interval
                        # 채널별로 다른 주파수와 위상의 사인파 생성
                        freq = 0.5 + ch * 0.2
                        phase = ch * (math.pi / 4)
                        amplitude = 2 + ch * 0.5 # 2V ~ 5.5V
                        noise = random.uniform(-0.1, 0.1)
                        voltage = amplitude * math.sin(2 * math.pi * freq * t + phase) + noise
                        results[ch] = {'voltage': voltage}

                if results:
                    self.data_queue.put({
                        'timestamp': datetime.now(),
                        'channels': results
                    })
                
                sample_count += 1
                time.sleep(self.sample_interval)

            except Exception as e:
                logging.error(f"Error in monitor loop: {e}")
                time.sleep(self.sample_interval)

    def start_update_loop(self):
        """GUI 업데이트 루프 시작"""
        self.update_gui()

    def update_gui(self):
        """GUI를 주기적으로 업데이트"""
        data_updated = False
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                self.data_manager.add_batch_data(data['timestamp'], data['channels'])
                data_updated = True
            except queue.Empty:
                break
        
        if data_updated:
            self.update_chart()
            self.update_statistics()

        # 50ms 마다 GUI 업데이트 스케줄링
        self.root.after(50, self.update_gui)

    def update_chart(self):
        """차트 업데이트"""
        y_limits = self.control_panel.get_y_scale_limits()
        all_channel_data = self.data_manager.get_all_data()
        
        # ControlPanel의 채널 활성화 상태에 따라 데이터 필터링
        display_data = {}
        for ch, data in all_channel_data.items():
            if self.control_panel.chart_channel_vars[ch].get():
                display_data[ch] = data
        
        self.chart_panel.update_time_domain(display_data, y_limits)


    def update_statistics(self):
        """통계 정보 업데이트"""
        stats_channel = self.control_panel.get_stats_channel()
        data = self.data_manager.get_channel_data(stats_channel)

        if data and len(data['voltages']) > 1:
            stats = self.statistics.calculate_statistics(data['voltages'])
            self.control_panel.update_statistics(stats)

    def on_closing(self):
        """윈도우 종료 시 처리"""
        logging.info("Closing application...")
        self.stop_monitoring()
        # 스레드가 완전히 종료될 시간을 잠시 줌
        time.sleep(0.2)
        self.root.destroy()

    def run(self):
        """애플리케이션 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    # 로깅 설정
    log_file_path = os.path.join(os.path.dirname(__file__), 'time_domain_viewer.log')
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)

    logging.info("Starting Time Domain Viewer Application")
    app = TimeDomainViewer()
    app.run()
