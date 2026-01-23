#!/usr/bin/env python3
"""
Data Manager Module
데이터 수집 및 관리
"""

from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataManager:
    """데이터 수집 및 관리 클래스"""

    def __init__(self, max_points=300):
        """
        Args:
            max_points: 채널당 최대 저장 포인트 수
        """
        self.max_points = max_points
        self.channel_data = {i: {
            'timestamps': deque(maxlen=max_points),
            'voltages': deque(maxlen=max_points),
            'enabled': False
        } for i in range(8)}

    def add_data(self, channel, timestamp, voltage):
        """데이터 추가"""
        if 0 <= channel <= 7:
            self.channel_data[channel]['timestamps'].append(timestamp)
            self.channel_data[channel]['voltages'].append(voltage)

    def add_batch_data(self, timestamp, channels_data):
        """
        배치 데이터 추가

        Args:
            timestamp: 측정 시간
            channels_data: {channel: {'voltage': value, ...}, ...}
        """
        for ch, data in channels_data.items():
            if self.channel_data[ch]['enabled']:
                self.add_data(ch, timestamp, data['voltage'])

    def enable_channel(self, channel, enabled=True):
        """채널 활성화/비활성화"""
        if 0 <= channel <= 7:
            self.channel_data[channel]['enabled'] = enabled

    def is_channel_enabled(self, channel):
        """채널 활성화 여부 확인"""
        if 0 <= channel <= 7:
            return self.channel_data[channel]['enabled']
        return False

    def clear_channel(self, channel):
        """채널 데이터 초기화"""
        if 0 <= channel <= 7:
            self.channel_data[channel]['timestamps'].clear()
            self.channel_data[channel]['voltages'].clear()

    def clear_all(self):
        """전체 데이터 초기화"""
        for ch in range(8):
            self.clear_channel(ch)

    def get_channel_data(self, channel):
        """채널 데이터 반환"""
        if 0 <= channel <= 7:
            return {
                'timestamps': list(self.channel_data[channel]['timestamps']),
                'voltages': list(self.channel_data[channel]['voltages']),
                'enabled': self.channel_data[channel]['enabled']
            }
        return None

    def get_all_data(self):
        """전체 데이터 반환"""
        return {ch: self.get_channel_data(ch) for ch in range(8)}

    def get_enabled_channels(self):
        """활성화된 채널 리스트 반환"""
        return [ch for ch in range(8) if self.channel_data[ch]['enabled']]

    def resize_buffer(self, max_points):
        """버퍼 크기 조정"""
        self.max_points = max_points
        for ch in range(8):
            old_ts = list(self.channel_data[ch]['timestamps'])
            old_v = list(self.channel_data[ch]['voltages'])

            self.channel_data[ch]['timestamps'] = deque(old_ts, maxlen=max_points)
            self.channel_data[ch]['voltages'] = deque(old_v, maxlen=max_points)
