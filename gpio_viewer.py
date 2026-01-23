#!/usr/bin/env python3
"""
GPIO Viewer
- ControlPanel의 GPIO Tab 내용을 구현한 독립 실행형 GUI
- UI 내 토글 스위치를 통해 '실제 하드웨어'와 '시뮬레이션' 모드 전환
"""
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import threading
import time
import random
from collections import defaultdict
import logging

# 기존 프로젝트 모듈 임포트
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.widgets.gpio_widget import GPIOStatusWidget, GPIOOutputWidget, GPIOAlarmWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 실제 하드웨어 라이브러리 import 시도
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False


class HybridGPIOMonitor:
    """
    실제 하드웨어 또는 시뮬레이션 모드로 동작하는 GPIO 모니터 클래스
    """
    PIN_ADCS = 8
    PIN_DOUT = 12
    PIN_DIN = 13
    PIN_GP5 = 5
    PIN_GP17 = 17
    PIN_GP22 = 22
    PIN_GP27 = 27
    INPUT_PINS = [PIN_DIN, PIN_GP5, PIN_GP17, PIN_GP22, PIN_GP27]
    OUTPUT_PINS = [PIN_DOUT]
    PIN_NAMES = {
        8: "CS (SPI)", 12: "DOUT", 13: "DIN (Alarm)", 5: "GPIO 5",
        17: "GPIO 17", 22: "GPIO 22", 27: "GPIO 27"
    }

    def __init__(self):
        self.running = False
        self.threads = []
        self.callbacks = []
        self.event_counts = defaultdict(lambda: {"rising": 0, "falling": 0, "total": 0})
        self.pin_states = {pin: False for pin in self.INPUT_PINS}
        self.last_event_time = defaultdict(float)
        # 초기 모드는 GPIO_AVAILABLE 여부에 따라 결정
        self.is_simulation_mode = not GPIO_AVAILABLE
        logging.info(f"HybridGPIOMonitor initialized. RPi.GPIO available: {GPIO_AVAILABLE}. Initial sim mode: {self.is_simulation_mode}")

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def _trigger_callbacks(self, pin, edge):
        for callback in self.callbacks:
            try:
                callback(pin, edge)
            except Exception as e:
                logging.error(f"Callback error: {e}")

    def start_monitoring(self, mode="simulation"):
        if self.running:
            return

        self.is_simulation_mode = (mode == "simulation")
        self.running = True
        
        target_loop = self._simulation_loop if self.is_simulation_mode else self._monitor_pin_real
        logging.info(f"Starting in {'SIMULATION' if self.is_simulation_mode else 'REAL HARDWARE'} mode.")

        if self.is_simulation_mode:
            sim_thread = threading.Thread(target=target_loop, daemon=True)
            sim_thread.start()
            self.threads.append(sim_thread)
        else: # Real Hardware Mode
            for pin in self.INPUT_PINS:
                t = threading.Thread(target=target_loop, args=(pin,), daemon=True)
                t.start()
                self.threads.append(t)
        
        logging.info(f"Monitoring started with {len(self.threads)} threads.")

    def stop_monitoring(self):
        if not self.running:
            return
            
        self.running = False
        logging.info("Stopping monitoring threads...")
        # 모든 스레드가 종료될 때까지 기다림
        active_threads = [t for t in self.threads if t.is_alive()]
        for t in active_threads:
            t.join(timeout=1.0)
        self.threads = []
        
        if GPIO_AVAILABLE and not self.is_simulation_mode:
            try:
                # cleanup은 한 번만 호출되어야 함
                GPIO.cleanup()
                logging.info("GPIO cleanup completed.")
            except Exception as e:
                # 이미 cleanup 되었을 경우 오류가 발생할 수 있음
                logging.warning(f"Could not perform GPIO cleanup: {e}")

        logging.info("Monitoring stopped.")

    def _simulation_loop(self):
        while self.running:
            pin_to_change = random.choice(self.INPUT_PINS)
            if random.random() < 0.2:
                new_state = not self.pin_states[pin_to_change]
                self.pin_states[pin_to_change] = new_state
                edge = "rising" if new_state else "falling"
                self.event_counts[pin_to_change][edge] += 1
                self.event_counts[pin_to_change]["total"] += 1
                self.last_event_time[pin_to_change] = time.time()
                self._trigger_callbacks(pin_to_change, edge)
            time.sleep(random.uniform(0.5, 2.0))

    def _monitor_pin_real(self, pin):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.pin_states[pin] = GPIO.input(pin) == GPIO.HIGH
            logging.info(f"Monitoring GPIO {pin} - Initial: {'HIGH' if self.pin_states[pin] else 'LOW'}")

            last_state = self.pin_states[pin]
            debounce_time = 0.1
            last_event_time = 0

            while self.running:
                current_state = GPIO.input(pin) == GPIO.HIGH
                current_time = time.time()
                if current_state != last_state:
                    if current_time - last_event_time > debounce_time:
                        last_event_time = current_time
                        last_state = current_state
                        self.pin_states[pin] = current_state
                        edge = "rising" if current_state else "falling"
                        self.event_counts[pin][edge] += 1
                        self.event_counts[pin]["total"] += 1
                        self.last_event_time[pin] = current_time
                        self._trigger_callbacks(pin, edge)
                time.sleep(0.02)
        except Exception as e:
            if self.running: # stop_monitoring 중에 발생하는 에러는 무시
                logging.error(f"Error monitoring real GPIO {pin}: {e}")

    def get_pin_state(self, pin):
        return self.pin_states.get(pin, False)

    def get_event_count(self, pin, edge=None):
        if edge is None:
            return self.event_counts[pin]["total"]
        return self.event_counts[pin].get(edge, 0)

    def get_last_event_time(self, pin):
        return self.last_event_time.get(pin, 0)

    def set_output(self, pin, state):
        if pin not in self.OUTPUT_PINS:
            return False
        
        if self.is_simulation_mode:
            logging.info(f"Simulated: Set output pin {pin} to {'HIGH' if state else 'LOW'}")
            return True
        else:
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
                logging.info(f"Real: Set output pin {pin} to {'HIGH' if state else 'LOW'}")
                return True
            except Exception as e:
                logging.error(f"Error setting real GPIO {pin}: {e}")
                return False

    def reset_counters(self):
        self.event_counts.clear()
        self.last_event_time.clear()
        logging.info("GPIO event counters reset.")

    def get_pin_name(self, pin):
        return self.PIN_NAMES.get(pin, f"GPIO {pin}")


class GPIOViewer:
    """GPIO Viewer Standalone Application"""

    def __init__(self):
        self.root = tb.Window(title="GPIO Viewer", themename="darkly", size=(400, 600))
        self.gpio_monitor = HybridGPIOMonitor()
        self.gpio_input_widgets = {}
        self.alarm_active = False
        self.alarm_channel = None
        self.alarm_count = 0
        self.last_alarm_time = 0

        self.setup_gui()
        self.gpio_monitor.register_callback(self.on_gpio_event)
        self._on_mode_change() # 초기 모드 설정 및 모니터링 시작
        self.update_gui()

    def setup_gui(self):
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        control_frame = tb.Frame(main_frame)
        control_frame.pack(fill=X, pady=(0, 10))

        # 모드 토글 스위치 및 라벨을 위한 서브 프레임 (중앙 정렬용)
        mode_control_frame = tb.Frame(control_frame)
        mode_control_frame.pack(anchor=CENTER) # 중앙 정렬

        self.mode_var = tk.BooleanVar(value=self.gpio_monitor.is_simulation_mode)
        self.mode_label_var = tk.StringVar() # 동적 텍스트용

        # 텍스트 라벨과 토글 버튼
        tb.Label(mode_control_frame, textvariable=self.mode_label_var, bootstyle="secondary").pack(side=LEFT, padx=(0, 5))
        mode_switch = tb.Checkbutton(
            mode_control_frame,
            variable=self.mode_var,
            command=self._on_mode_change,
            bootstyle="round-toggle"
        )
        mode_switch.pack(side=LEFT) # 라벨 옆에 배치
        
        if not GPIO_AVAILABLE:
            mode_switch.config(state=DISABLED) # RPi.GPIO 없으면 토글 비활성화

        self._update_mode_switch_text() # 초기 텍스트 설정
        
        canvas = tk.Canvas(main_frame, highlightthickness=0, bg=self.root.cget('bg'))
        scrollbar = tb.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        input_frame = tb.Labelframe(scrollable_frame, text="Input Pins", padding=10, bootstyle="info")
        input_frame.pack(fill=X, pady=5, padx=10)
        for pin in HybridGPIOMonitor.INPUT_PINS:
            name = self.gpio_monitor.get_pin_name(pin)
            widget = GPIOStatusWidget(input_frame, pin, name)
            widget.pack(fill=X, pady=2)
            self.gpio_input_widgets[pin] = widget

        output_frame = tb.Labelframe(scrollable_frame, text="Output Pins", padding=10, bootstyle="success")
        output_frame.pack(fill=X, pady=5, padx=10)
        cs_widget = GPIOStatusWidget(output_frame, HybridGPIOMonitor.PIN_ADCS, "CS (SPI)")
        cs_widget.pack(fill=X, pady=2)
        self.gpio_input_widgets[HybridGPIOMonitor.PIN_ADCS] = cs_widget
        for pin in HybridGPIOMonitor.OUTPUT_PINS:
            name = self.gpio_monitor.get_pin_name(pin)
            widget = GPIOOutputWidget(output_frame, pin, name, on_toggle=self.on_gpio_output_toggle)
            widget.pack(fill=X, pady=2)

        alarm_frame = tb.Labelframe(scrollable_frame, text="ADC Alarm", padding=10, bootstyle="warning")
        alarm_frame.pack(fill=X, pady=5, padx=10)
        self.gpio_alarm_widget = GPIOAlarmWidget(alarm_frame)
        self.gpio_alarm_widget.pack(fill=X)

        reset_frame = tb.Frame(scrollable_frame, padding=10)
        reset_frame.pack(fill=X)
        tb.Button(reset_frame, text="Reset Event Counters", command=self.on_reset_gpio_counters, bootstyle="secondary").pack(fill=X)

    def _update_mode_switch_text(self):
        """모드 스위치 텍스트를 현재 모드에 따라 업데이트"""
        if self.mode_var.get(): # True이면 시뮬레이션 모드 활성화
            self.mode_label_var.set("Simul Mode")
        else:
            self.mode_label_var.set("Real Mode")

    def _on_mode_change(self):
        self.gpio_monitor.stop_monitoring()
        self.on_reset_gpio_counters()
        new_mode = "simulation" if self.mode_var.get() else "real"
        self.gpio_monitor.start_monitoring(new_mode)
        self._update_mode_switch_text() # 텍스트 업데이트

    def on_gpio_event(self, pin, edge):
        if pin == HybridGPIOMonitor.PIN_DIN and edge == "falling":
            self.alarm_active = True
            self.alarm_count += 1
            self.last_alarm_time = time.time()
            self.alarm_channel = random.randint(0, 7)
            logging.warning(f"ADC Alarm on CH{self.alarm_channel}")

    def update_gui(self):
        if self.root.winfo_exists():
            if self.gpio_monitor.running:
                for pin, widget in self.gpio_input_widgets.items():
                    state = self.gpio_monitor.get_pin_state(pin)
                    count = self.gpio_monitor.get_event_count(pin)
                    last_time = self.gpio_monitor.get_last_event_time(pin)
                    widget.update_state(state, count, last_time)
                
                if self.gpio_monitor.is_simulation_mode:
                    self.gpio_input_widgets[HybridGPIOMonitor.PIN_ADCS].update_state(True)

                self.gpio_alarm_widget.update_alarm(
                    self.alarm_active, self.alarm_channel, self.last_alarm_time, self.alarm_count
                )
                if self.alarm_active and (time.time() - self.last_alarm_time) > 3.0:
                    self.alarm_active = False; self.alarm_channel = None
            
            self.root.after(500, self.update_gui)

    def on_gpio_output_toggle(self, pin, state):
        return self.gpio_monitor.set_output(pin, state)

    def on_reset_gpio_counters(self):
        self.gpio_monitor.reset_counters()
        self.alarm_count = 0
        self.last_alarm_time = 0
        logging.info("All counters have been reset.")

    def on_closing(self):
        # 모니터링을 먼저 중지하고 윈도우를 파괴
        self.gpio_monitor.stop_monitoring()
        self.root.destroy()
        logging.info("GPIO Viewer application closed.")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    log_file_path = os.path.join(os.path.dirname(__file__), 'gpio_viewer.log')
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    logging.info("Starting GPIO Viewer Application")
    app = GPIOViewer()
    app.run()
