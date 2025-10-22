#!/usr/bin/env python3
"""
ADS8668 ADC Controller Module
하드웨어 제어 레이어
"""

import spidev
import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)


class ADS8668Controller:
    """ADS8668 ADC 제어 클래스"""

    RANGES = {
        0: {"name": "±10V", "reg": 0, "offset": 0x800, "scale": 5.00},
        1: {"name": "±5V", "reg": 1, "offset": 0x800, "scale": 2.50},
        2: {"name": "±2.5V", "reg": 2, "offset": 0x800, "scale": 1.25},
        3: {"name": "±1.25V", "reg": 3, "offset": 0x800, "scale": 0.625},
        4: {"name": "±0.5V", "reg": 11, "offset": 0x800, "scale": 0.3125},
        5: {"name": "0-10V", "reg": 5, "offset": 0x000, "scale": 2.50},
        6: {"name": "0-5V", "reg": 6, "offset": 0x000, "scale": 1.25},
        7: {"name": "0-2.5V", "reg": 7, "offset": 0x000, "scale": 0.625},
        8: {"name": "0-1.25V", "reg": 15, "offset": 0x000, "scale": 0.3125},
    }

    ADCS_PIN = 8

    def __init__(self):
        self.spi = None
        self.channel_ranges = [0] * 8
        self.is_connected = False

    def connect(self):
        """ADC 연결 및 초기화"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.ADCS_PIN, GPIO.OUT, initial=GPIO.HIGH)

            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.no_cs = True
            self.spi.mode = 1
            self.spi.max_speed_hz = 10000000

            time.sleep(0.5)
            self.is_connected = True
            logger.info("ADS8668 연결 성공")
            return True
        except Exception as e:
            logger.error(f"ADS8668 연결 실패: {e}")
            return False

    def _xfer_spi(self, data):
        """SPI 데이터 전송"""
        GPIO.output(self.ADCS_PIN, 0)
        result = self.spi.xfer(data)
        GPIO.output(self.ADCS_PIN, 1)
        return result

    def set_channel_range(self, channel, range_id):
        """채널 입력 레인지 설정"""
        if channel < 0 or channel > 7 or range_id not in self.RANGES:
            return False
        try:
            reg_value = self.RANGES[range_id]["reg"]
            wdat = [((5 + channel) << 1) | 1, reg_value, 0x00, 0x00]
            self._xfer_spi(wdat)
            self.channel_ranges[channel] = range_id
            logger.info(f"CH{channel} 레인지 설정: {self.RANGES[range_id]['name']}")
            return True
        except Exception as e:
            logger.error(f"레인지 설정 실패: {e}")
            return False

    def read_channel(self, channel):
        """단일 채널 읽기"""
        if channel < 0 or channel > 7:
            return None
        try:
            wdat = [0xc0 + (channel << 2), 0x00, 0x00, 0x00]
            self._xfer_spi(wdat)
            rdat = self._xfer_spi(wdat)
            adat = (rdat[2] << 4) + (rdat[3] >> 4)

            range_id = self.channel_ranges[channel]
            range_info = self.RANGES[range_id]
            voltage = (adat - range_info["offset"]) * range_info["scale"] / 1000

            return {"raw": adat, "voltage": voltage, "range": range_info["name"]}
        except Exception as e:
            logger.error(f"CH{channel} 읽기 실패: {e}")
            return None

    def read_all_channels(self):
        """전체 채널 읽기"""
        results = {}
        for ch in range(8):
            data = self.read_channel(ch)
            if data:
                results[ch] = data
        return results

    def close(self):
        """연결 종료"""
        if self.spi:
            self.spi.close()
        GPIO.cleanup()
        self.is_connected = False
        logger.info("ADS8668 연결 종료")
