#!/usr/bin/env python3
"""
Signal Statistics Module
신호 통계 분석
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class SignalStatistics:
    """신호 통계 계산 클래스"""

    @staticmethod
    def rms(data):
        """
        RMS (Root Mean Square) 계산

        Args:
            data: 신호 데이터 배열

        Returns:
            RMS 값
        """
        if len(data) == 0:
            return 0.0
        arr = np.array(data)
        return np.sqrt(np.mean(arr ** 2))

    @staticmethod
    def peak_to_peak(data):
        """
        Peak-to-Peak 값 계산

        Args:
            data: 신호 데이터 배열

        Returns:
            P-P 값
        """
        if len(data) == 0:
            return 0.0
        arr = np.array(data)
        return np.max(arr) - np.min(arr)

    @staticmethod
    def calculate_statistics(data):
        """
        기본 통계 계산

        Args:
            data: 신호 데이터 배열

        Returns:
            {'rms', 'max', 'min', 'avg', 'pp'} 딕셔너리
        """
        if len(data) == 0:
            return {
                'rms': 0.0,
                'max': 0.0,
                'min': 0.0,
                'avg': 0.0,
                'pp': 0.0
            }

        arr = np.array(data)
        return {
            'rms': np.sqrt(np.mean(arr ** 2)),
            'max': np.max(arr),
            'min': np.min(arr),
            'avg': np.mean(arr),
            'pp': np.max(arr) - np.min(arr)
        }

    @staticmethod
    def thd(spectrum, fundamental_idx, num_harmonics=5):
        """
        THD (Total Harmonic Distortion) 계산

        Args:
            spectrum: FFT 스펙트럼 (magnitude)
            fundamental_idx: 기본 주파수 인덱스
            num_harmonics: 고려할 고조파 개수

        Returns:
            THD (dB)
        """
        try:
            fundamental = spectrum[fundamental_idx]
            harmonics_power = 0.0

            for i in range(2, num_harmonics + 2):
                harmonic_idx = fundamental_idx * i
                if harmonic_idx < len(spectrum):
                    harmonics_power += spectrum[harmonic_idx] ** 2

            thd_ratio = np.sqrt(harmonics_power) / fundamental
            thd_db = 20 * np.log10(thd_ratio) if thd_ratio > 0 else -120
            return thd_db

        except Exception as e:
            logger.error(f"THD 계산 실패: {e}")
            return 0.0

    @staticmethod
    def snr(spectrum, signal_idx, noise_floor_idxs):
        """
        SNR (Signal-to-Noise Ratio) 계산

        Args:
            spectrum: FFT 스펙트럼
            signal_idx: 신호 인덱스
            noise_floor_idxs: 노이즈 플로어 인덱스 범위

        Returns:
            SNR (dB)
        """
        try:
            signal_power = spectrum[signal_idx] ** 2
            noise_power = np.mean(spectrum[noise_floor_idxs] ** 2)

            snr_ratio = signal_power / noise_power if noise_power > 0 else 0
            snr_db = 10 * np.log10(snr_ratio) if snr_ratio > 0 else -120
            return snr_db

        except Exception as e:
            logger.error(f"SNR 계산 실패: {e}")
            return 0.0

    @staticmethod
    def sinad(spectrum, signal_idx):
        """
        SINAD (Signal-to-Noise and Distortion) 계산

        Args:
            spectrum: FFT 스펙트럼
            signal_idx: 신호 인덱스

        Returns:
            SINAD (dB)
        """
        try:
            signal_power = spectrum[signal_idx] ** 2
            total_power = np.sum(spectrum ** 2)
            noise_distortion_power = total_power - signal_power

            sinad_ratio = signal_power / noise_distortion_power if noise_distortion_power > 0 else 0
            sinad_db = 10 * np.log10(sinad_ratio) if sinad_ratio > 0 else -120
            return sinad_db

        except Exception as e:
            logger.error(f"SINAD 계산 실패: {e}")
            return 0.0

    @staticmethod
    def enob(sinad_db):
        """
        ENOB (Effective Number of Bits) 계산

        Args:
            sinad_db: SINAD 값 (dB)

        Returns:
            ENOB (bits)
        """
        return (sinad_db - 1.76) / 6.02

    @staticmethod
    def sfdr(spectrum, signal_idx):
        """
        SFDR (Spurious-Free Dynamic Range) 계산

        Args:
            spectrum: FFT 스펙트럼
            signal_idx: 신호 인덱스

        Returns:
            SFDR (dB)
        """
        try:
            signal = spectrum[signal_idx]

            # 신호를 제외한 나머지에서 최대값 찾기
            spectrum_copy = spectrum.copy()
            spectrum_copy[signal_idx] = 0
            max_spur = np.max(spectrum_copy)

            sfdr_db = 20 * np.log10(signal / max_spur) if max_spur > 0 else 120
            return sfdr_db

        except Exception as e:
            logger.error(f"SFDR 계산 실패: {e}")
            return 0.0
