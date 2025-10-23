#!/usr/bin/env python3
"""
GPIO Monitor Module
GPIO 입력/출력 모니터링 (gpiod 기반)
"""

import threading
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# gpiod가 설치되어 있는지 확인
try:
    import gpiod
    GPIOD_AVAILABLE = True
except ImportError:
    GPIOD_AVAILABLE = False
    logger.warning("gpiod not available - GPIO monitoring disabled")

# RPi.GPIO fallback
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available - GPIO output control disabled")


class GPIOMonitor:
    """GPIO 입력/출력 모니터링 클래스"""

    # GPIO 핀 정의 (wdaqV3_SampleCode.py 기반)
    PIN_ADCS = 8    # SPI Chip Select (OUTPUT)
    PIN_DOUT = 12   # 디지털 출력 (OUTPUT)
    PIN_DIN = 13    # 디지털 입력 / ADC 알람 (INPUT)
    PIN_GP5 = 5     # 범용 입력 (INPUT)
    PIN_GP17 = 17   # 범용 입력 (INPUT)
    PIN_GP22 = 22   # 범용 입력 (INPUT)
    PIN_GP27 = 27   # 범용 입력 (INPUT)

    # 입력 핀 목록
    INPUT_PINS = [PIN_DIN, PIN_GP5, PIN_GP17, PIN_GP22, PIN_GP27]

    # 출력 핀 목록 (CS는 ADC에서 제어하므로 제외)
    OUTPUT_PINS = [PIN_DOUT]

    # 핀 이름 매핑
    PIN_NAMES = {
        8: "CS (SPI)",
        12: "DOUT",
        13: "DIN (Alarm)",
        5: "GPIO 5",
        17: "GPIO 17",
        22: "GPIO 22",
        27: "GPIO 27"
    }

    def __init__(self, enable_monitoring=True):
        """
        GPIO 모니터 초기화

        Args:
            enable_monitoring: True이면 입력 모니터링 활성화
        """
        self.enable_monitoring = enable_monitoring
        self.running = False
        self.threads = []

        # 이벤트 카운터 (핀별)
        self.event_counts = defaultdict(lambda: {"rising": 0, "falling": 0, "total": 0})

        # 핀 상태 (True=HIGH, False=LOW)
        self.pin_states = {}

        # 마지막 이벤트 시각
        self.last_event_time = defaultdict(float)

        # 콜백 함수들
        self.callbacks = []

        # gpiod 사용 가능 여부
        self.use_gpiod = GPIOD_AVAILABLE and enable_monitoring

        # RPi.GPIO 사용 가능 여부 (출력 제어용)
        self.use_rpi_gpio = GPIO_AVAILABLE

        # 초기 상태 설정
        for pin in self.INPUT_PINS:
            self.pin_states[pin] = False  # 초기값 LOW

        logger.info(f"GPIOMonitor initialized (gpiod: {self.use_gpiod}, RPi.GPIO: {self.use_rpi_gpio})")

    def register_callback(self, callback):
        """
        GPIO 이벤트 콜백 등록

        Args:
            callback: 콜백 함수 (pin, edge) 인자 받음
        """
        self.callbacks.append(callback)

    def _trigger_callbacks(self, pin, edge):
        """콜백 함수들 실행"""
        for callback in self.callbacks:
            try:
                callback(pin, edge)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def _monitor_pin_gpiod(self, pin):
        """
        gpiod 기반 핀 모니터링 (별도 스레드)

        Args:
            pin: GPIO 핀 번호
        """
        try:
            chip = gpiod.Chip("gpiochip0")
            line = chip.get_line(pin)

            # INPUT으로 요청하여 초기 상태 읽기
            line.request(consumer="ads8668-monitor", type=gpiod.LINE_REQ_DIR_IN)

            # 초기 상태 읽기
            initial_state = line.get_value() == 1
            self.pin_states[pin] = initial_state
            logger.info(f"Started monitoring GPIO {pin} ({self.PIN_NAMES.get(pin, 'Unknown')}) - Initial state: {'HIGH' if initial_state else 'LOW'}")

            # 이벤트 감지 모드로 재요청
            line.release()
            line.request(consumer="ads8668-monitor", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

            debounce_time = 0.05  # 50ms 디바운스
            last_event = 0
            poll_counter = 0

            while self.running:
                # 1초 타임아웃으로 이벤트 대기
                if line.event_wait(timeout=1.0):
                    event = line.event_read()
                    current_time = time.time()

                    # 디바운스 처리
                    if current_time - last_event < debounce_time:
                        continue

                    last_event = current_time

                    # 이벤트 타입 확인
                    if event.type == gpiod.LineEvent.RISING_EDGE:
                        edge = "rising"
                        state = True
                    else:
                        edge = "falling"
                        state = False

                    # 상태 업데이트
                    self.pin_states[pin] = state
                    self.event_counts[pin][edge] += 1
                    self.event_counts[pin]["total"] += 1
                    self.last_event_time[pin] = current_time

                    # 콜백 실행
                    self._trigger_callbacks(pin, edge)

                    logger.debug(f"GPIO {pin} {edge} edge detected (total: {self.event_counts[pin]['total']})")
                else:
                    # 타임아웃 발생 - 주기적으로 현재 상태 폴링 (10초마다)
                    poll_counter += 1
                    if poll_counter >= 10:  # 10초마다 상태 읽기
                        poll_counter = 0
                        # 이벤트 모드에서는 직접 읽을 수 없으므로 재요청
                        try:
                            line.release()
                            line.request(consumer="ads8668-monitor", type=gpiod.LINE_REQ_DIR_IN)
                            current_state = line.get_value() == 1

                            # 상태가 변경되었으면 업데이트 (이벤트 놓친 경우)
                            if current_state != self.pin_states[pin]:
                                logger.warning(f"GPIO {pin} state mismatch detected - updating to {'HIGH' if current_state else 'LOW'}")
                                self.pin_states[pin] = current_state

                            line.release()
                            line.request(consumer="ads8668-monitor", type=gpiod.LINE_REQ_EV_BOTH_EDGES)
                        except Exception as e:
                            logger.error(f"Error polling GPIO {pin}: {e}")

        except Exception as e:
            logger.error(f"Error monitoring GPIO {pin}: {e}")

    def _monitor_pin_polling(self, pin):
        """
        폴링 방식 핀 모니터링 (gpiod 없을 때 대체)

        Args:
            pin: GPIO 핀 번호
        """
        logger.warning(f"GPIO {pin} monitoring disabled (gpiod not available)")
        # 실제 하드웨어 없이도 GUI가 동작하도록 더미 상태 유지
        while self.running:
            time.sleep(1)

    def start_monitoring(self):
        """GPIO 입력 모니터링 시작"""
        if not self.enable_monitoring:
            logger.info("GPIO monitoring disabled")
            return False

        if self.running:
            logger.warning("GPIO monitoring already running")
            return False

        self.running = True

        # 각 입력 핀마다 별도 스레드 생성
        for pin in self.INPUT_PINS:
            if self.use_gpiod:
                target = self._monitor_pin_gpiod
            else:
                target = self._monitor_pin_polling

            t = threading.Thread(target=target, args=(pin,), daemon=True)
            t.start()
            self.threads.append(t)

        logger.info(f"GPIO monitoring started ({len(self.threads)} threads)")
        return True

    def stop_monitoring(self):
        """GPIO 입력 모니터링 중지"""
        if not self.running:
            return

        self.running = False

        # 스레드 종료 대기
        for t in self.threads:
            t.join(timeout=2.0)

        self.threads.clear()
        logger.info("GPIO monitoring stopped")

    def get_pin_state(self, pin):
        """
        핀 상태 조회

        Args:
            pin: GPIO 핀 번호

        Returns:
            bool: True=HIGH, False=LOW
        """
        return self.pin_states.get(pin, False)

    def get_event_count(self, pin, edge=None):
        """
        이벤트 카운트 조회

        Args:
            pin: GPIO 핀 번호
            edge: 'rising', 'falling', None(전체)

        Returns:
            int: 이벤트 횟수
        """
        if edge is None:
            return self.event_counts[pin]["total"]
        return self.event_counts[pin].get(edge, 0)

    def get_last_event_time(self, pin):
        """
        마지막 이벤트 발생 시각

        Args:
            pin: GPIO 핀 번호

        Returns:
            float: 시간 (time.time() 형식), 이벤트 없으면 0
        """
        return self.last_event_time.get(pin, 0)

    def get_all_pin_states(self):
        """
        모든 입력 핀 상태 조회

        Returns:
            dict: {pin: state}
        """
        return {pin: self.get_pin_state(pin) for pin in self.INPUT_PINS}

    def set_output(self, pin, state):
        """
        출력 핀 제어

        Args:
            pin: GPIO 핀 번호
            state: True=HIGH, False=LOW

        Returns:
            bool: 성공 여부
        """
        if not self.use_rpi_gpio:
            logger.warning("RPi.GPIO not available - cannot control output")
            return False

        if pin not in self.OUTPUT_PINS:
            logger.error(f"GPIO {pin} is not configured as output")
            return False

        try:
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)

            # 핀이 설정되어 있지 않으면 설정
            try:
                GPIO.setup(pin, GPIO.OUT)
            except:
                pass

            GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
            logger.info(f"GPIO {pin} set to {'HIGH' if state else 'LOW'}")
            return True

        except Exception as e:
            logger.error(f"Error setting GPIO {pin}: {e}")
            return False

    def reset_counters(self):
        """이벤트 카운터 리셋"""
        self.event_counts.clear()
        self.last_event_time.clear()
        logger.info("GPIO event counters reset")

    def get_pin_name(self, pin):
        """
        핀 이름 조회

        Args:
            pin: GPIO 핀 번호

        Returns:
            str: 핀 이름
        """
        return self.PIN_NAMES.get(pin, f"GPIO {pin}")

    def close(self):
        """GPIO 모니터 종료"""
        self.stop_monitoring()
        logger.info("GPIOMonitor closed")
