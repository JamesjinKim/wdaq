#!/usr/bin/env python3
"""
Main Window Module
메인 윈도우 통합
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import time
import queue
from datetime import datetime

from gui.panels.header_panel import HeaderPanel
from gui.panels.channel_panel import ChannelPanel
from gui.panels.chart_panel import ChartPanel
from gui.panels.control_panel import ControlPanel
from gui.panels.status_bar import StatusBar

from hardware.adc_controller import ADS8668Controller
from hardware.gpio_monitor import GPIOMonitor
from data.data_manager import DataManager
from data.data_export import DataExporter
from utils.config_manager import ConfigManager
from analysis.statistics import SignalStatistics

import logging
logger = logging.getLogger(__name__)


class MainWindow:
    """ADS8668 모니터 메인 윈도우"""

    def __init__(self):
        # 하드웨어 및 데이터 관리
        self.adc = ADS8668Controller()
        self.gpio_monitor = GPIOMonitor(enable_monitoring=True)
        self.data_manager = DataManager(max_points=300)
        self.config_manager = ConfigManager()
        self.data_exporter = DataExporter()
        self.statistics = SignalStatistics()

        # 모니터링 상태
        self.is_monitoring = False
        self.monitor_thread = None
        self.data_queue = queue.Queue()

        # 설정
        self.sample_interval = 3.0  # 초기 샘플링 인터벌 3초
        self.chart_time_window = 5

        # GPIO 알람 상태
        self.alarm_active = False
        self.alarm_channel = None
        self.alarm_count = 0
        self.last_alarm_time = 0

        # GUI 초기화
        self.setup_gui()
        self.connect_adc()
        self.start_gpio_monitoring()
        self.start_update_loop()

    def setup_gui(self):
        """GUI 구성"""
        self.root = tb.Window(
            title="ADS8668 ADC Monitor - Modular",
            themename="darkly",
            size=(1400, 800),
            resizable=(True, True)
        )

        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)

        # 헤더 패널
        self.header_panel = HeaderPanel(main_frame, {
            'on_start_stop': self.toggle_monitoring,
            'on_save_config': self.save_config,
            'on_load_config': self.load_config,
            'on_save_data': self.save_data,
            'on_interval_change': self.update_sample_interval
        })
        self.header_panel.pack(fill=X, pady=(0, 10))

        # 중앙 컨텐츠 (3단 분할)
        content_frame = tb.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=(10, 0))

        # 좌측: 채널 패널
        left_frame = tb.Frame(content_frame, width=400)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 5))
        left_frame.pack_propagate(False)

        self.channel_panel = ChannelPanel(
            left_frame,
            ADS8668Controller.RANGES,
            self.on_channel_enable,
            self.on_channel_range_change
        )
        self.channel_panel.pack(fill=BOTH, expand=True)

        # 중앙: 차트 패널
        center_frame = tb.Frame(content_frame)
        center_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

        self.chart_panel = ChartPanel(
            center_frame,
            chart_type='time_domain',
            time_window=self.chart_time_window
        )
        self.chart_panel.pack(fill=BOTH, expand=True)

        # 우측: 컨트롤 패널 (GPIO 텍스트 표시를 위해 너비 확대)
        right_frame = tb.Frame(content_frame, width=360)
        right_frame.pack(side=RIGHT, fill=Y, padx=(5, 0))
        right_frame.pack_propagate(False)

        self.control_panel = ControlPanel(right_frame, {
            'on_scale_change': self.on_scale_mode_change,
            'on_apply_custom_scale': self.on_apply_custom_scale,
            'on_cursor_toggle': self.on_cursor_toggle,
            'on_save_snapshot': self.save_chart_snapshot,
            'on_channel_display_toggle': self.on_channel_display_toggle,
            'on_gpio_output_toggle': self.on_gpio_output_toggle,
            'on_reset_gpio_counters': self.on_reset_gpio_counters
        })
        self.control_panel.pack(fill=BOTH, expand=True)

        # 하단: 상태바
        self.status_bar = StatusBar(main_frame)
        self.status_bar.pack(fill=X, pady=(10, 0))

    def connect_adc(self):
        """ADC 연결"""
        logger.info("-" * 60)
        logger.info("Connecting to ADS8668...")
        if self.adc.connect():
            self.header_panel.set_connection_status(True)
            self.status_bar.set_status("ADC connected successfully")
            self.status_bar.set_sample_rate(self.sample_interval)  # 초기 샘플 레이트 표시
            # 기본 레인지 설정
            for ch in range(8):
                self.adc.set_channel_range(ch, 0)
            logger.info("✓ ADC connected successfully")
            logger.info(f"  Sample interval: {self.sample_interval}s")
            logger.info("-" * 60)
        else:
            self.header_panel.set_connection_status(False)
            logger.error("✗ Failed to connect to ADS8668")
            messagebox.showerror("Error", "Failed to connect to ADS8668")

    def on_channel_enable(self, channel, enabled):
        """채널 활성화 콜백"""
        self.data_manager.enable_channel(channel, enabled)
        self.control_panel.set_channel_display(channel, enabled)
        logger.info(f"CH{channel} {'enabled' if enabled else 'disabled'}")

    def on_channel_range_change(self, channel, range_name):
        """채널 레인지 변경 콜백"""
        for range_id, info in ADS8668Controller.RANGES.items():
            if info["name"] == range_name:
                self.adc.set_channel_range(channel, range_id)
                break

    def on_channel_display_toggle(self, channel, enabled):
        """차트 채널 표시 토글"""
        self.data_manager.enable_channel(channel, enabled)
        self.channel_panel.set_channel_enabled(channel, enabled)

    def on_scale_mode_change(self, mode):
        """Y-Scale 모드 변경"""
        self.status_bar.set_status(f"Y-Scale mode: {mode}")

    def on_apply_custom_scale(self, y_min, y_max):
        """커스텀 Y-Scale 적용"""
        if y_min >= y_max:
            messagebox.showwarning("Invalid Input", "Y-Min must be less than Y-Max")
            return
        self.status_bar.set_status(f"Custom Y-Scale: [{y_min:.4f}, {y_max:.4f}]")

    def on_cursor_toggle(self, enabled):
        """커서 토글"""
        self.chart_panel.enable_cursor(enabled)
        self.status_bar.set_status(f"Cursor {'enabled' if enabled else 'disabled'}")

    def update_sample_interval(self, interval):
        """측정 주기 업데이트"""
        if 0.1 <= interval <= 10.0:
            self.sample_interval = interval
            self.status_bar.set_sample_rate(interval)
            self.status_bar.set_status(f"Sample interval: {interval:.1f}s")
        else:
            messagebox.showwarning("Invalid Input", "Interval: 0.1-10.0 seconds")

    def toggle_monitoring(self):
        """모니터링 시작/중지"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """모니터링 시작"""
        if not self.adc.is_connected:
            messagebox.showwarning("Warning", "ADC not connected!")
            return

        self.is_monitoring = True
        self.header_panel.set_monitoring_state(True)
        self.status_bar.set_status("Monitoring...")

        logger.info("=" * 60)
        logger.info("▶ ADC Monitoring STARTED")
        logger.info(f"  Interval: {self.sample_interval}s")
        enabled_ch = [ch for ch in range(8) if self.data_manager.channel_data[ch]['enabled']]
        logger.info(f"  Enabled channels: {enabled_ch}")
        logger.info("=" * 60)

        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        self.header_panel.set_monitoring_state(False)
        self.status_bar.set_status("Stopped")

        logger.info("=" * 60)
        logger.info("■ ADC Monitoring STOPPED")
        logger.info("=" * 60)

    def monitor_loop(self):
        """모니터링 루프 (별도 스레드)"""
        sample_count = 0
        while self.is_monitoring:
            try:
                results = self.adc.read_all_channels()
                if results:
                    sample_count += 1
                    self.data_queue.put({
                        'timestamp': datetime.now(),
                        'channels': results
                    })

                    # ADC 전압 값 로그 출력 (활성화된 채널만)
                    enabled_channels = [ch for ch in range(8) if self.data_manager.channel_data[ch]['enabled']]
                    if enabled_channels:
                        log_msg = f"[ADC #{sample_count:04d}] "
                        for ch in enabled_channels:
                            if ch in results:
                                voltage = results[ch]['voltage']
                                log_msg += f"CH{ch}:{voltage:+7.4f}V  "
                        logger.info(log_msg.rstrip())

                time.sleep(self.sample_interval)
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(self.sample_interval)

    def start_update_loop(self):
        """GUI 업데이트 루프"""
        self.update_gui()

    def update_gui(self):
        """GUI 업데이트"""
        # 시간 업데이트
        self.status_bar.update_time()

        # 데이터 큐 처리
        data_updated = False
        while not self.data_queue.empty():
            try:
                data = self.data_queue.get_nowait()
                self.data_manager.add_batch_data(data['timestamp'], data['channels'])

                # 채널 표시 업데이트
                for ch, ch_data in data['channels'].items():
                    if self.data_manager.channel_data[ch]['enabled']:
                        # 프로그레스바 계산
                        range_id = self.adc.channel_ranges[ch]
                        range_info = ADS8668Controller.RANGES[range_id]
                        max_v = float(range_info['name'].split('V')[0].replace('±', '').replace('-', ''))

                        if '±' in range_info['name']:
                            pct = ((ch_data['voltage'] + max_v) / (2 * max_v)) * 100
                        else:
                            pct = (ch_data['voltage'] / max_v) * 100

                        self.channel_panel.update_channel_display(
                            ch, ch_data['voltage'], pct
                        )

                data_updated = True
            except queue.Empty:
                break

        # 차트 및 통계 업데이트
        if data_updated:
            self.update_chart()
            self.update_statistics()

        # GPIO 상태 업데이트
        self.update_gpio_status()

        # 500ms마다 반복
        self.root.after(500, self.update_gui)

    def update_chart(self):
        """차트 업데이트"""
        y_limits = self.control_panel.get_y_scale_limits()
        channel_data = self.data_manager.get_all_data()
        self.chart_panel.update_time_domain(channel_data, y_limits)

    def update_statistics(self):
        """통계 업데이트"""
        stats_channel = self.control_panel.get_stats_channel()
        data = self.data_manager.get_channel_data(stats_channel)

        if data and len(data['voltages']) > 0:
            stats = self.statistics.calculate_statistics(data['voltages'])
            self.control_panel.update_statistics(stats)

    def save_chart_snapshot(self):
        """차트 스냅샷 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"chart_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )

        if filename:
            try:
                self.chart_panel.save_snapshot(filename)
                self.status_bar.set_status(f"Chart saved: {filename}")
                messagebox.showinfo("Success", f"Chart snapshot saved!\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chart:\n{e}")

    def save_data(self):
        """데이터 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            channel_data = self.data_manager.get_all_data()
            if self.data_exporter.export_to_csv(filename, channel_data):
                messagebox.showinfo("Success", f"Data saved!\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to save data")

    def save_config(self):
        """설정 저장"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            # 현재 설정 수집
            config = self.config_manager.save_to_dict()
            config['sample_interval'] = self.sample_interval
            config['chart_time_window'] = self.chart_time_window

            # 채널 설정
            channel_states = self.channel_panel.get_all_states()
            config['channels'] = [
                {
                    'enabled': channel_states[ch]['enabled'],
                    'range': channel_states[ch]['range']
                } for ch in range(8)
            ]

            if self.data_exporter.export_config(filename, config):
                self.status_bar.set_status("Config saved")
            else:
                messagebox.showerror("Error", "Failed to save config")

    def load_config(self):
        """설정 불러오기"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            config = self.data_exporter.import_config(filename)
            if config:
                # 설정 적용
                if 'sample_interval' in config:
                    self.header_panel.set_interval(config['sample_interval'])
                    self.update_sample_interval(config['sample_interval'])

                # 채널 설정 적용
                for ch in range(8):
                    ch_cfg = config['channels'][ch]
                    self.channel_panel.set_channel_enabled(ch, ch_cfg['enabled'])
                    self.channel_panel.set_channel_range(ch, ch_cfg['range'])
                    self.on_channel_enable(ch, ch_cfg['enabled'])
                    self.on_channel_range_change(ch, ch_cfg['range'])

                self.status_bar.set_status("Config loaded")
            else:
                messagebox.showerror("Error", "Failed to load config")

    def start_gpio_monitoring(self):
        """GPIO 모니터링 시작"""
        logger.info("-" * 60)
        logger.info("Starting GPIO monitoring...")

        # GPIO 이벤트 콜백 등록
        self.gpio_monitor.register_callback(self.on_gpio_event)

        # 모니터링 시작
        if self.gpio_monitor.start_monitoring():
            logger.info("✓ GPIO monitoring started")
            logger.info(f"  Monitoring pins: {', '.join([str(p) for p in self.gpio_monitor.INPUT_PINS])}")
            logger.info("-" * 60)
        else:
            logger.warning("✗ GPIO monitoring not available (gpiod not installed)")
            logger.info("-" * 60)

    def on_gpio_event(self, pin, edge):
        """
        GPIO 이벤트 콜백

        Args:
            pin: GPIO 핀 번호
            edge: 'rising' 또는 'falling'
        """
        logger.info(f"GPIO {pin} {edge} edge detected")

        # DIN 핀 (13번)에서 falling edge 감지 시 ADC 알람으로 처리
        if pin == 13 and edge == "falling":
            self.alarm_active = True
            self.alarm_count += 1
            self.last_alarm_time = time.time()
            # 실제로는 ADC 레지스터를 읽어서 어느 채널인지 확인해야 함
            # 여기서는 간단히 처리
            self.alarm_channel = 0  # 임시

    def update_gpio_status(self):
        """GPIO 상태 업데이트 (500ms마다 호출)"""
        # 모든 입력 핀 상태 업데이트
        for pin in GPIOMonitor.INPUT_PINS:
            state = self.gpio_monitor.get_pin_state(pin)
            event_count = self.gpio_monitor.get_event_count(pin)
            last_event_time = self.gpio_monitor.get_last_event_time(pin)

            self.control_panel.update_gpio_input(
                pin, state, event_count, last_event_time
            )

        # CS 핀 상태도 업데이트 (읽기 전용)
        # CS 핀은 ADC 컨트롤러에서 제어하므로 상태만 표시
        # ADC가 연결되어 있고 SPI 통신 중일 때는 HIGH (대부분의 시간)
        if self.adc.is_connected:
            # CS 핀은 기본적으로 HIGH 상태 유지
            self.control_panel.update_gpio_input(8, True, 0, 0)
        else:
            self.control_panel.update_gpio_input(8, False, 0, 0)

        # 알람 상태 업데이트
        self.control_panel.update_gpio_alarm(
            active=self.alarm_active,
            channel=self.alarm_channel,
            last_time=self.last_alarm_time,
            total_count=self.alarm_count
        )

        # 알람이 활성 상태이고 일정 시간 지났으면 비활성화
        if self.alarm_active and (time.time() - self.last_alarm_time) > 5.0:
            self.alarm_active = False

    def on_gpio_output_toggle(self, pin, state):
        """
        GPIO 출력 토글 콜백

        Args:
            pin: GPIO 핀 번호
            state: True=HIGH, False=LOW

        Returns:
            bool: 성공 여부
        """
        success = self.gpio_monitor.set_output(pin, state)
        if success:
            self.status_bar.set_status(
                f"GPIO {pin} set to {'HIGH' if state else 'LOW'}"
            )
        else:
            self.status_bar.set_status(
                f"Failed to set GPIO {pin}"
            )
        return success

    def on_reset_gpio_counters(self):
        """GPIO 이벤트 카운터 리셋"""
        self.gpio_monitor.reset_counters()
        self.alarm_count = 0
        self.last_alarm_time = 0
        self.status_bar.set_status("GPIO event counters reset")

    def on_closing(self):
        """프로그램 종료"""
        if self.is_monitoring:
            self.stop_monitoring()
            time.sleep(1)
        if self.gpio_monitor:
            self.gpio_monitor.close()
        if self.adc:
            self.adc.close()
        self.root.destroy()

    def run(self):
        """실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
