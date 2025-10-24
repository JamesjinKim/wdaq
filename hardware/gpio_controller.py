"""
GPIO Controller for Digital I/O
Manages GPIO pins for digital input and output operations
"""

import logging
import threading
import time
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    import gpiod
    HAS_GPIO = True
except (ImportError, RuntimeError):
    HAS_GPIO = False
    logger.warning("GPIO 라이브러리를 사용할 수 없습니다 (Raspberry Pi가 아니거나 라이브러리 미설치)")


class GPIOController:
    """GPIO 디지털 입출력 컨트롤러"""

    # GPIO 핀 번호 정의 (BCM 모드)
    OUTPUT_PIN_23 = 23  # 디지털 출력 1
    OUTPUT_PIN_24 = 24  # 디지털 출력 2
    INPUT_PIN_13 = 13   # 디지털 입력

    def __init__(self):
        """GPIO 컨트롤러 초기화"""
        self.is_connected = False
        self.output_states = {
            self.OUTPUT_PIN_23: False,
            self.OUTPUT_PIN_24: False
        }
        self.input_state = False
        self.event_callback = None
        self.monitor_thread = None
        self.running = False

    def connect(self):
        """GPIO 초기화 및 연결"""
        if not HAS_GPIO:
            logger.error("GPIO 라이브러리가 없습니다")
            return False

        try:
            # GPIO 모드 설정 (중복 설정 방지)
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)

            GPIO.setwarnings(False)

            # 출력 핀 설정
            GPIO.setup(self.OUTPUT_PIN_23, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.OUTPUT_PIN_24, GPIO.OUT, initial=GPIO.LOW)

            # 입력 핀 설정
            GPIO.setup(self.INPUT_PIN_13, GPIO.IN, pull_up_down=GPIO.PUD_OFF)

            # 초기 상태 읽기
            self.input_state = GPIO.input(self.INPUT_PIN_13)

            self.is_connected = True
            logger.info("GPIO 초기화 완료")
            return True

        except Exception as e:
            logger.error(f"GPIO 초기화 실패: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """GPIO 정리 및 연결 해제"""
        if self.is_connected:
            try:
                self.stop_input_monitoring()
                # GPIO.cleanup()은 메인 프로그램 종료 시에만 호출
                self.is_connected = False
                logger.info("GPIO 연결 해제 완료")
            except Exception as e:
                logger.error(f"GPIO 연결 해제 실패: {e}")

    def set_output(self, pin, state):
        """
        디지털 출력 핀 상태 설정

        Args:
            pin: GPIO 핀 번호 (23 또는 24)
            state: True(HIGH/ON) 또는 False(LOW/OFF)

        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected:
            logger.warning("GPIO가 연결되지 않았습니다")
            return False

        if pin not in self.output_states:
            logger.error(f"잘못된 GPIO 핀 번호: {pin}")
            return False

        try:
            GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
            self.output_states[pin] = state
            logger.info(f"GPIO {pin} 출력: {'HIGH' if state else 'LOW'}")
            return True
        except Exception as e:
            logger.error(f"GPIO {pin} 출력 설정 실패: {e}")
            return False

    def get_output_state(self, pin):
        """
        디지털 출력 핀 상태 조회

        Args:
            pin: GPIO 핀 번호 (23 또는 24)

        Returns:
            bool: 현재 상태 (True=HIGH, False=LOW)
        """
        return self.output_states.get(pin, False)

    def get_input_state(self):
        """
        디지털 입력 핀 상태 조회

        Returns:
            bool: 현재 상태 (True=HIGH, False=LOW)
        """
        if not self.is_connected:
            return False

        try:
            self.input_state = GPIO.input(self.INPUT_PIN_13)
            return self.input_state
        except Exception as e:
            logger.error(f"GPIO 입력 상태 읽기 실패: {e}")
            return False

    def start_input_monitoring(self, callback=None):
        """
        디지털 입력 핀 감시 시작 (gpiod 사용)

        Args:
            callback: 이벤트 발생 시 호출할 함수 (pin, edge, timestamp)
        """
        if not self.is_connected:
            logger.warning("GPIO가 연결되지 않았습니다")
            return False

        if self.running:
            logger.warning("입력 감시가 이미 실행 중입니다")
            return False

        self.event_callback = callback
        self.running = True

        # gpiod 기반 모니터링 스레드 시작
        self.monitor_thread = threading.Thread(
            target=self._monitor_input_gpiod,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("GPIO 입력 감시 시작")
        return True

    def stop_input_monitoring(self):
        """디지털 입력 핀 감시 중지"""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
            logger.info("GPIO 입력 감시 중지")

    def _monitor_input_gpiod(self):
        """gpiod를 사용한 GPIO 입력 감시 (별도 스레드)"""
        try:
            chip = gpiod.Chip("gpiochip0")
            line = chip.get_line(self.INPUT_PIN_13)
            line.request(consumer="gpio-monitor", type=gpiod.LINE_REQ_EV_BOTH_EDGES)

            last_event_time = 0
            debounce_time = 0.2  # 200ms 디바운스

            logger.info(f"GPIO {self.INPUT_PIN_13} 입력 감시 스레드 시작")

            while self.running:
                if line.event_wait(timeout=1):
                    event = line.event_read()
                    current_time = time.time()

                    # 디바운스 처리
                    if current_time - last_event_time > debounce_time:
                        edge = "rising" if event.type == gpiod.LineEvent.RISING_EDGE else "falling"
                        state = "HIGH" if edge == "rising" else "LOW"
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # 상태 업데이트
                        self.input_state = (edge == "rising")

                        logger.info(f"GPIO {self.INPUT_PIN_13} 이벤트: {state}")

                        # 콜백 함수 호출
                        if self.event_callback:
                            self.event_callback(self.INPUT_PIN_13, edge, timestamp)

                        last_event_time = current_time

            line.release()

        except Exception as e:
            logger.error(f"GPIO 입력 감시 중 오류: {e}")
        finally:
            logger.info("GPIO 입력 감시 스레드 종료")

    def get_all_states(self):
        """
        모든 GPIO 핀 상태 조회

        Returns:
            dict: 모든 핀의 현재 상태
        """
        return {
            'outputs': {
                23: self.output_states[self.OUTPUT_PIN_23],
                24: self.output_states[self.OUTPUT_PIN_24]
            },
            'input': {
                13: self.get_input_state()
            }
        }
