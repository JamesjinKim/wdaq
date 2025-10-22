#!/usr/bin/env python3
"""
Data Export Module
데이터 내보내기 (CSV, JSON 등)
"""

import csv
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """데이터 내보내기 클래스"""

    @staticmethod
    def export_to_csv(filename, channel_data):
        """
        CSV 파일로 내보내기

        Args:
            filename: 저장할 파일명
            channel_data: {ch: {'timestamps': [...], 'voltages': [...], 'enabled': bool}, ...}
        """
        try:
            # 활성화된 채널만 필터링
            enabled_channels = [ch for ch in range(8) if channel_data[ch]['enabled']]

            if not enabled_channels:
                logger.warning("활성화된 채널이 없습니다")
                return False

            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)

                # 헤더 작성
                header = ['Timestamp'] + [f'CH{ch} (V)' for ch in enabled_channels]
                writer.writerow(header)

                # 최대 길이 계산
                max_len = max([len(channel_data[ch]['timestamps'])
                              for ch in enabled_channels], default=0)

                # 데이터 작성
                for i in range(max_len):
                    row = []
                    ts = None
                    for ch in enabled_channels:
                        if i < len(channel_data[ch]['timestamps']):
                            if ts is None:
                                ts = channel_data[ch]['timestamps'][i].strftime('%Y-%m-%d %H:%M:%S.%f')
                            row.append(f"{channel_data[ch]['voltages'][i]:.6f}")
                        else:
                            row.append("")
                    if ts:
                        writer.writerow([ts] + row)

            logger.info(f"데이터 저장 성공: {filename}")
            return True

        except Exception as e:
            logger.error(f"CSV 저장 실패: {e}")
            return False

    @staticmethod
    def export_config(filename, config):
        """
        설정을 JSON 파일로 저장

        Args:
            filename: 저장할 파일명
            config: 설정 딕셔너리
        """
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"설정 저장 성공: {filename}")
            return True
        except Exception as e:
            logger.error(f"설정 저장 실패: {e}")
            return False

    @staticmethod
    def import_config(filename):
        """
        JSON 설정 파일 불러오기

        Args:
            filename: 불러올 파일명

        Returns:
            설정 딕셔너리 또는 None
        """
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            logger.info(f"설정 불러오기 성공: {filename}")
            return config
        except Exception as e:
            logger.error(f"설정 불러오기 실패: {e}")
            return None
