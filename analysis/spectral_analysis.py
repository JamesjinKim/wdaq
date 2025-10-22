#!/usr/bin/env python3
"""
Spectral Analysis Module
주파수 영역 신호 분석 (FFT, Harmonics)
ch2.png 참조
"""

import numpy as np
try:
    from scipy import signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from analysis.statistics import SignalStatistics
import logging

logger = logging.getLogger(__name__)


class SpectralAnalyzer:
    """주파수 영역 신호 분석 클래스"""

    WINDOWS = {
        'Rectangular': np.ones,
        'Hann': np.hanning,
        'Hamming': np.hamming,
        'Blackman': np.blackman,
        'Bartlett': np.bartlett,
    }

    if SCIPY_AVAILABLE:
        WINDOWS['7 Term B-Harris'] = signal.windows.blackmanharris

    def __init__(self):
        self.stats = SignalStatistics()

    def compute_fft(self, data, fs, window='Hann', dc_remove=True):
        """
        FFT 계산

        Args:
            data: 시간 영역 데이터
            fs: 샘플링 주파수 (Hz)
            window: 윈도우 함수 이름
            dc_remove: DC 성분 제거 여부

        Returns:
            (frequencies, magnitude, phase) 튜플
        """
        if len(data) < 2:
            return None, None, None

        try:
            arr = np.array(data)

            # DC 제거
            if dc_remove:
                arr = arr - np.mean(arr)

            # 윈도우 적용
            if window in self.WINDOWS:
                window_func = self.WINDOWS[window](len(arr))
                arr = arr * window_func

            # FFT 계산
            fft_result = np.fft.rfft(arr)
            frequencies = np.fft.rfftfreq(len(arr), 1 / fs)
            magnitude = np.abs(fft_result)
            phase = np.angle(fft_result)

            return frequencies, magnitude, phase

        except Exception as e:
            logger.error(f"FFT 계산 실패: {e}")
            return None, None, None

    def compute_psd(self, data, fs, window='Hann'):
        """
        PSD (Power Spectral Density) 계산

        Args:
            data: 시간 영역 데이터
            fs: 샘플링 주파수
            window: 윈도우 함수

        Returns:
            (frequencies, psd) 튜플
        """
        try:
            freqs, magnitude, _ = self.compute_fft(data, fs, window)

            if freqs is None:
                return None, None

            # PSD 계산 (magnitude^2)
            psd = (magnitude ** 2) / len(data)

            return freqs, psd

        except Exception as e:
            logger.error(f"PSD 계산 실패: {e}")
            return None, None

    def to_db(self, magnitude, ref=1.0):
        """
        Magnitude를 dB로 변환

        Args:
            magnitude: 크기 값
            ref: 기준 값

        Returns:
            dB 값
        """
        with np.errstate(divide='ignore'):
            db = 20 * np.log10(magnitude / ref)
            db[np.isinf(db)] = -120  # -inf를 -120dB로 제한
        return db

    def find_fundamental(self, frequencies, magnitude, min_freq=10, max_freq=None):
        """
        기본 주파수 찾기

        Args:
            frequencies: 주파수 배열
            magnitude: 크기 배열
            min_freq: 최소 주파수
            max_freq: 최대 주파수

        Returns:
            (fundamental_freq, fundamental_idx) 튜플
        """
        try:
            # 주파수 범위 필터링
            mask = frequencies >= min_freq
            if max_freq:
                mask = mask & (frequencies <= max_freq)

            filtered_mag = magnitude.copy()
            filtered_mag[~mask] = 0

            # 최대값 찾기
            fundamental_idx = np.argmax(filtered_mag)
            fundamental_freq = frequencies[fundamental_idx]

            return fundamental_freq, fundamental_idx

        except Exception as e:
            logger.error(f"기본 주파수 찾기 실패: {e}")
            return 0, 0

    def find_harmonics(self, frequencies, magnitude, fundamental_freq, num_harmonics=9):
        """
        고조파 찾기

        Args:
            frequencies: 주파수 배열
            magnitude: 크기 배열
            fundamental_freq: 기본 주파수
            num_harmonics: 찾을 고조파 개수

        Returns:
            [(harmonic_order, freq, magnitude), ...] 리스트
        """
        harmonics = []

        try:
            for n in range(1, num_harmonics + 1):
                target_freq = fundamental_freq * n

                # 가장 가까운 주파수 찾기
                idx = np.argmin(np.abs(frequencies - target_freq))
                freq = frequencies[idx]
                mag = magnitude[idx]

                harmonics.append((n, freq, mag))

        except Exception as e:
            logger.error(f"고조파 찾기 실패: {e}")

        return harmonics

    def analyze_spectrum(self, data, fs, window='7 Term B-Harris', num_harmonics=9):
        """
        전체 스펙트럼 분석 (ch2.png 참조)

        Args:
            data: 시간 영역 데이터
            fs: Device Fs (샘플링 주파수)
            window: 윈도우 함수
            num_harmonics: 고조파 개수

        Returns:
            분석 결과 딕셔너리
        """
        freqs, mag, phase = self.compute_fft(data, fs, window)

        if freqs is None:
            return None

        # 기본 주파수 찾기
        fund_freq, fund_idx = self.find_fundamental(freqs, mag)

        # 고조파 찾기
        harmonics = self.find_harmonics(freqs, mag, fund_freq, num_harmonics)

        # dB 변환
        mag_db = self.to_db(mag)

        # 통계 계산
        snr = self.stats.snr(mag, fund_idx, range(len(mag) // 2, len(mag)))
        thd = self.stats.thd(mag, fund_idx, num_harmonics)
        sinad = self.stats.sinad(mag, fund_idx)
        sfdr = self.stats.sfdr(mag, fund_idx)
        enob = self.stats.enob(sinad)

        # 신호 파워 계산 (dBFS)
        signal_power = mag_db[fund_idx] if fund_idx < len(mag_db) else -120

        return {
            'frequencies': freqs,
            'magnitude': mag,
            'magnitude_db': mag_db,
            'phase': phase,
            'fundamental': {
                'frequency': fund_freq,
                'index': fund_idx,
                'magnitude': mag[fund_idx] if fund_idx < len(mag) else 0
            },
            'harmonics': harmonics,
            'metrics': {
                'SNR': snr,
                'THD': thd,
                'SFDR': sfdr,
                'SINAD': sinad,
                'ENOB': enob,
                'Signal_Power_dBFS': signal_power
            },
            'parameters': {
                'device_fs': fs,
                'window': window,
                'num_harmonics': num_harmonics,
                'samples': len(data)
            }
        }
