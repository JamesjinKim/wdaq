#!/usr/bin/env python3
"""
Configuration Manager Module
설정 관리
"""

import json
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """설정 관리 클래스"""

    DEFAULT_CONFIG = {
        'sample_interval': 1.0,
        'chart_time_window': 5,
        'max_points': 300,
        'chart_y_scale_mode': 'Auto mode',
        'chart_y_min': -12.0,
        'chart_y_max': 12.0,
        'channels': [
            {
                'enabled': False,
                'range': '±10V'
            } for _ in range(8)
        ]
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()

    def get(self, key, default=None):
        """설정 값 가져오기"""
        return self.config.get(key, default)

    def set(self, key, value):
        """설정 값 설정"""
        self.config[key] = value

    def get_channel_config(self, channel):
        """채널 설정 가져오기"""
        if 0 <= channel <= 7:
            return self.config['channels'][channel]
        return None

    def set_channel_config(self, channel, enabled=None, range_name=None):
        """채널 설정 업데이트"""
        if 0 <= channel <= 7:
            if enabled is not None:
                self.config['channels'][channel]['enabled'] = enabled
            if range_name is not None:
                self.config['channels'][channel]['range'] = range_name

    def save_to_dict(self):
        """현재 설정을 딕셔너리로 반환"""
        return self.config.copy()

    def load_from_dict(self, config_dict):
        """딕셔너리로부터 설정 불러오기"""
        try:
            # 기본 설정과 병합
            for key in self.DEFAULT_CONFIG:
                if key in config_dict:
                    self.config[key] = config_dict[key]
            logger.info("설정 불러오기 성공")
            return True
        except Exception as e:
            logger.error(f"설정 불러오기 실패: {e}")
            return False

    def reset_to_default(self):
        """기본 설정으로 초기화"""
        self.config = self.DEFAULT_CONFIG.copy()
        logger.info("설정이 기본값으로 초기화되었습니다")
