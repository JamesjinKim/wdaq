# ADS8668 ADC Monitor - Modular Version

8채널 ADC (ADS8668) 모니터링 프로그램 - 모듈화된 구조

---

## 📋 목차

- [프로젝트 구조](#프로젝트-구조)
- [주요 기능](#주요-기능)
- [실행 방법](#실행-방법)
- [의존성 설치](#의존성-설치)
- [GUI 사용법](#gui-사용법)
- [문제 해결](#문제-해결)
- [모듈 설명](#모듈-설명)
- [확장 방법](#확장-방법)

---

## 프로젝트 구조

```
ads8668_monitor/
├── main.py                         # 메인 진입점
├── run.sh                          # 실행 스크립트
├── requirements.txt                # 의존성 목록
│
├── hardware/                       # 하드웨어 계층
│   ├── __init__.py
│   └── adc_controller.py          # ADS8668 SPI 통신 및 제어
│
├── data/                          # 데이터 관리 계층
│   ├── __init__.py
│   ├── data_manager.py            # 실시간 데이터 버퍼 관리
│   └── data_export.py             # CSV/JSON 입출력
│
├── analysis/                      # 신호 분석 계층
│   ├── __init__.py
│   ├── statistics.py              # 통계 계산 (RMS, THD, SNR, SINAD, ENOB)
│   ├── time_domain.py             # 시간 영역 분석
│   └── spectral_analysis.py       # 주파수 분석 (FFT, Harmonics)
│
├── utils/                         # 유틸리티 계층
│   ├── __init__.py
│   ├── config_manager.py          # 설정 관리
│   └── logger.py                  # 로깅 설정
│
└── gui/                           # GUI 계층
    ├── __init__.py
    ├── main_window.py             # 메인 윈도우 통합
    │
    ├── panels/                    # GUI 패널들
    │   ├── __init__.py
    │   ├── header_panel.py        # 상단 헤더 (연결 상태, 제어 버튼)
    │   ├── channel_panel.py       # 채널 설정 패널 (8채널 관리)
    │   ├── chart_panel.py         # 차트 표시 패널
    │   ├── control_panel.py       # 차트 컨트롤 및 통계
    │   └── status_bar.py          # 하단 상태바
    │
    └── widgets/                   # 재사용 위젯
        ├── __init__.py
        ├── channel_widget.py      # 개별 채널 위젯
        └── chart_widget.py        # 차트 위젯 (Time/Spectral)
```

---

## 주요 기능

### 1. Time Domain Display (ch1.png 참조)
- ✅ 실시간 8채널 전압 모니터링
- ✅ 채널별 활성화/비활성화
- ✅ Y-Scale 자동/수동 조정 (Auto, ±10V, ±5V, Custom 등)
- ✅ 측정 커서 기능
- ✅ 통계 계산 (RMS, Max, Min, Avg, P-P)
- ✅ 차트 스냅샷 저장 (PNG/PDF)

### 2. Spectral Analysis (ch2.png 참조) - 준비됨
- ⭐ FFT 주파수 분석
- ⭐ Harmonics 검출 (최대 9개)
- ⭐ 윈도우 함수 선택 (Hann, Hamming, Blackman, B-Harris)
- ⭐ 신호 품질 측정:
  - SNR (Signal-to-Noise Ratio)
  - THD (Total Harmonic Distortion)
  - SFDR (Spurious-Free Dynamic Range)
  - SINAD (Signal-to-Noise And Distortion)
  - ENOB (Effective Number of Bits)

### 3. 데이터 관리
- 💾 CSV 데이터 내보내기
- 💿 JSON 설정 저장/불러오기
- 📸 차트 스냅샷 저장 (PNG/PDF)

---

## 실행 방법

### 방법 1: 직접 실행 (권장)
```bash
cd /home/drjins/shinho/Egicon/wdaq/ads8668_monitor
python3 main.py
```

### 방법 2: 실행 스크립트 사용
```bash
cd /home/drjins/shinho/Egicon/wdaq/ads8668_monitor
./run.sh
```

### 방법 3: 상위 디렉토리에서 실행
```bash
cd /home/drjins/shinho/Egicon/wdaq
python3 -c "import sys; sys.path.insert(0, 'ads8668_monitor'); from gui.main_window import MainWindow; app = MainWindow(); app.run()"
```

### 실행 확인

프로그램을 실행하면 다음과 같은 메시지가 표시됩니다:

**성공적인 실행**:
```
2025-10-21 15:25:52 - ads8668_monitor - INFO - ADS8668 Monitor Starting...
```

**하드웨어 연결 실패 (정상)**:
```
ADS8668 연결 실패: 'GPIO busy'
```

> **참고**: GPIO busy 오류는 하드웨어가 다른 프로세스에서 사용 중이거나, 실제 ADS8668이 연결되어 있지 않아도 발생할 수 있습니다. GUI는 정상적으로 표시됩니다.

---

## 의존성 설치

### 필수 패키지

```bash
pip3 install -r requirements.txt
```

또는 개별 설치:

```bash
pip3 install ttkbootstrap matplotlib numpy spidev RPi.GPIO
```

### 패키지 목록

**필수**:
- Python 3.7+
- ttkbootstrap - Modern GUI framework
- matplotlib - 차트 그리기
- numpy - 수치 계산
- spidev - SPI 통신
- RPi.GPIO - GPIO 제어

**선택 (고급 신호 분석)**:
- scipy - 고급 윈도우 함수 (B-Harris 등)

---

## GUI 사용법

### 1. 채널 설정
- 좌측 패널에서 각 채널(CH0-CH7)을 활성화
- **ON** 토글 스위치 클릭
- 레인지 선택: ±10V, ±5V, ±2.5V, ±1.25V, 0-10V, 0-5V 등

### 2. 모니터링 시작
- 상단 **▶️ Start** 버튼 클릭
- 실시간 데이터 수집 시작
- 차트에 데이터 표시
- **Interval**: 측정 주기 설정 (0.1~10.0초)

### 3. 차트 제어
- **Y-Scale**:
  - Auto mode: 자동 범위 조정
  - ±10V Full, ±5V Full: 프리셋
  - Custom: 수동 입력
- **Enable Cursor**: 측정 커서 활성화
- **Channel Display**: 표시할 채널 선택/해제
- **툴바**: 줌, 팬, 홈 버튼 사용 가능

### 4. 통계 확인
- 우측 패널 **Statistics** 섹션
- 채널 선택 후 통계 확인:
  - **RMS**: Root Mean Square
  - **Max**: 최대값
  - **Min**: 최소값
  - **Avg**: 평균값
  - **P-P**: Peak-to-Peak

### 5. 데이터 저장
- **💾 Save Data**: CSV 파일로 데이터 저장
- **💿 Save Config**: 현재 설정을 JSON으로 저장
- **📂 Load**: 저장된 설정 불러오기
- **📸 Save Snapshot**: 차트를 이미지로 저장 (PNG/PDF)

---

## 문제 해결

### Import 오류
```
ImportError: No module named 'ttkbootstrap'
```
**해결**:
```bash
pip3 install ttkbootstrap
```

### GPIO 오류
```
RuntimeError: Not running on a RPi!
```
**해결**: 라즈베리파이에서만 실행 가능합니다. 개발 시에는 mock 모듈 사용 필요.

### SPI 오류
```
FileNotFoundError: [Errno 2] No such file or directory: '/dev/spidev0.0'
```
**해결**: SPI를 활성화하거나, ADS8668 하드웨어를 연결하세요.
```bash
sudo raspi-config
# Interface Options → SPI → Enable
```

### Permission 오류
```
PermissionError: [Errno 13] Permission denied: '/dev/spidev0.0'
```
**해결**:
```bash
sudo usermod -a -G spi,gpio $USER
# 재로그인 필요
```

또는 sudo로 실행:
```bash
sudo python3 main.py
```

### Python 버전 확인
```bash
python3 --version  # 3.7 이상 필요
```

### 패키지 설치 확인
```bash
pip3 list | grep -E 'ttkbootstrap|matplotlib|numpy'
```

---

## 모듈 설명

### Hardware Layer (`hardware/`)
- **adc_controller.py**: ADS8668 하드웨어 제어
  - SPI 통신 관리
  - 채널 레인지 설정 (±10V ~ ±0.5V, 0-10V ~ 0-1.25V)
  - ADC 데이터 읽기
  - 전압 값 계산

### Data Layer (`data/`)
- **data_manager.py**: 실시간 데이터 버퍼 관리
  - 채널별 데이터 deque 관리 (최대 300포인트)
  - 데이터 추가/삭제
  - 채널 활성화/비활성화
- **data_export.py**: CSV/JSON 파일 입출력
  - CSV 데이터 내보내기
  - JSON 설정 저장/불러오기

### Analysis Layer (`analysis/`)
- **statistics.py**: 신호 통계 계산
  - 기본 통계: RMS, Max, Min, Avg, P-P
  - 신호 품질: THD, SNR, SINAD, SFDR, ENOB
- **time_domain.py**: 시간 영역 신호 분석
  - 통계 분석
  - 피크 검출
  - 주파수 추정
- **spectral_analysis.py**: 주파수 영역 분석 (ch2.png 참조)
  - FFT 계산
  - 고조파 검출
  - 스펙트럼 분석

### GUI Layer (`gui/`)
- **main_window.py**: 전체 GUI 통합 및 로직
- **panels/**: 각 기능별 패널 모듈
  - header_panel.py: 상단 헤더
  - channel_panel.py: 8채널 관리
  - chart_panel.py: 차트 표시
  - control_panel.py: 컨트롤 및 통계
  - status_bar.py: 상태바
- **widgets/**: 재사용 가능한 UI 컴포넌트
  - channel_widget.py: 개별 채널 위젯
  - chart_widget.py: 차트 위젯

### Utils Layer (`utils/`)
- **config_manager.py**: 설정 관리
- **logger.py**: 로깅 설정

---

## 확장 방법

### Spectral Analysis 화면 추가

1. **새 패널 생성**:
```python
# gui/panels/spectral_panel.py
from gui.widgets.chart_widget import SpectralChart
from analysis.spectral_analysis import SpectralAnalyzer

class SpectralPanel:
    def __init__(self, parent):
        self.chart = SpectralChart(parent)
        self.analyzer = SpectralAnalyzer()

    def analyze_signal(self, data, fs):
        result = self.analyzer.analyze_spectrum(data, fs)
        self.chart.update_spectrum(
            result['frequencies'],
            result['magnitude_db'],
            result['harmonics']
        )
```

2. **메인 윈도우에서 탭 추가**:
```python
# main_window.py
from tkinter import ttk

# 탭 위젯 생성
self.tabs = ttk.Notebook(center_frame)

# Time Domain 탭
time_tab = tb.Frame(self.tabs)
self.chart_panel = ChartPanel(time_tab, chart_type='time_domain')
self.tabs.add(time_tab, text="Time Domain")

# Spectral 탭
spectral_tab = tb.Frame(self.tabs)
self.spectral_panel = SpectralPanel(spectral_tab)
self.tabs.add(spectral_tab, text="Spectral Analysis")
```

### 새로운 분석 기능 추가

```python
# analysis/custom_analysis.py 생성
class CustomAnalyzer:
    def analyze(self, data):
        # 분석 로직
        pass
```

### Spectral Analysis 사용 예시

```python
from analysis.spectral_analysis import SpectralAnalyzer

analyzer = SpectralAnalyzer()
result = analyzer.analyze_spectrum(data, fs=1000, window='Hann', num_harmonics=9)

print(f"SNR: {result['metrics']['SNR']:.2f} dB")
print(f"THD: {result['metrics']['THD']:.2f} dB")
print(f"SINAD: {result['metrics']['SINAD']:.2f} dB")
print(f"ENOB: {result['metrics']['ENOB']:.2f} bits")
```

---

## 로그 확인

실행 중 문제가 발생하면 로그를 확인하세요:

```bash
# 콘솔에 표시되는 로그
python3 main.py

# 파일로 저장 (선택)
python3 main.py 2>&1 | tee ads8668_monitor.log
```

---

## 추가 문서

- [STRUCTURE.md](STRUCTURE.md) - 모듈 구조 상세, 마이그레이션 가이드, 프로젝트 요약

---

## 라이선스

MIT License

---

## 개발자

Egicon Project Team

---

## 버전 정보

- **Version**: 2.0 (Modular)
- **From**: gui_wdaq3.py (900줄 단일 파일)
- **To**: 27개 모듈 (3,648줄)
- **Date**: 2025-10-21
