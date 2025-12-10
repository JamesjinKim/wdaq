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
    │   ├── control_panel.py       # 차트 컨트롤 및 통계 (탭: Statistics/GPIO/Digital I/O)
    │   ├── digital_io_panel.py    # 디지털 입출력 제어 패널
    │   └── status_bar.py          # 하단 상태바
    │
    └── widgets/                   # 재사용 위젯
        ├── __init__.py
        ├── channel_widget.py      # 개별 채널 위젯
        ├── chart_widget.py        # 차트 위젯 (Time/Spectral)
        └── gpio_widget.py         # GPIO 상태/제어 위젯
```

---

## 주요 기능

### 1. Time Domain Display
- ✅ 실시간 8채널 전압 모니터링
- ✅ 채널별 활성화/비활성화 (간단한 체크박스)
- ✅ Y-Scale 자동/수동 조정 (Auto, ±10V, ±5V, Custom 등)
- ✅ 프리셋 모드에서도 값 수정 가능 (Enter 키 적용)
- ✅ 측정 커서 기능
- ✅ 통계 계산 (RMS, Max, Min, Avg, P-P)
- ✅ 차트 스냅샷 저장 (PNG/PDF)
- ✅ 실시간 모니터링 최적화 (NavigationToolbar 제거)

### 2. Spectral Analysis - 준비됨
- ⭐ FFT 주파수 분석
- ⭐ Harmonics 검출 (최대 9개)
- ⭐ 윈도우 함수 선택 (Hann, Hamming, Blackman, B-Harris)
- ⭐ 신호 품질 측정:
  - SNR (Signal-to-Noise Ratio)
  - THD (Total Harmonic Distortion)
  - SFDR (Spurious-Free Dynamic Range)
  - SINAD (Signal-to-Noise And Distortion)
  - ENOB (Effective Number of Bits)

### 3. GPIO 및 Digital I/O 제어 ✨ (신규)
- ✅ **Digital Output 제어**
  - GPIO 23, 24 출력 제어 (ON/OFF 버튼)
  - 실시간 상태 표시 (HIGH/LOW)
- ✅ **Digital Input 모니터링**
  - GPIO 13 입력 상태 감시
  - Rising/Falling 엣지 감지
  - 이벤트 로그 기록
  - Start/Stop Monitoring 제어
- ✅ **GPIO 상태 모니터링**
  - GPIO 5, 17, 22, 27 입력 감시
  - GPIO 8 (CS) 상태 표시
  - 이벤트 카운터 및 통계
  - ADC 알람 감지 (GPIO 13)

### 4. 데이터 관리
- CSV 데이터 내보내기
- JSON 설정 저장/불러오기
- 차트 스냅샷 저장 (PNG/PDF)

### 5. Raspberry Pi 최적화
- 이모지 제거 (텍스트만 사용)
- 불필요한 UI 요소 제거
- 실시간 모니터링에 최적화된 깔끔한 인터페이스
- 하드웨어 연결 없이도 GUI 테스트 가능 (Test Mode)

---

## 실행 방법

### 방법 1: 실행 스크립트 사용 (권장)
```bash
./run.sh
```

### 방법 2: 가상 환경 수동 실행
```bash
source venv/bin/activate
python3 main.py
```

> **중요**: Raspberry Pi OS의 최신 버전에서는 가상 환경 사용이 필수입니다. 위 방법들은 자동으로 가상 환경을 활성화합니다.

### 실행 확인

프로그램을 실행하면 다음과 같은 메시지가 표시됩니다:

**성공적인 실행**:
```
2025-10-21 15:25:52 - ads8668_monitor - INFO - ADS8668 Monitor Starting...
```

**하드웨어 연결 실패 (정상)**:
```
ADS8668 연결 실패: [Errno 2] No such file or directory
✗ Failed to connect to ADS8668 (GUI test mode enabled)
```

> **참고**:
> - ADS8668이 실제로 연결되지 않은 경우 위 메시지가 표시됩니다.
> - **시뮬레이션 모드**: Start 버튼 클릭 시 "시뮬레이션 모드로 실행하시겠습니까?" 대화상자가 표시됩니다.
>   - "예" 선택: 사인파 + 노이즈 데이터로 GUI 테스트 가능
>   - "아니오" 선택: 모니터링 취소
> - 실제 하드웨어 연결 시에는 자동으로 ADC 모드로 동작합니다.

---

## 의존성 설치

### 자동 설치 (권장)

패키지는 이미 가상 환경에 설치되어 있습니다. 새로운 환경에서 설치하려면:

```bash
# 가상 환경 생성 (최초 1회만)
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate

# 패키지 설치
pip3 install -r requirements.txt
```

> **참고**: Raspberry Pi OS Bookworm 이상에서는 시스템 Python 보호를 위해 가상 환경 사용이 필수입니다 (PEP 668).

### 패키지 목록

**필수**:
- Python 3.7+
- ttkbootstrap - Modern GUI framework
- matplotlib - 차트 그리기
- numpy - 수치 계산
- spidev - SPI 통신
- RPi.GPIO - GPIO 제어 (레거시)
- gpiod - 최신 GPIO 제어 라이브러리

**선택 (고급 신호 분석)**:
- scipy - 고급 윈도우 함수 (B-Harris 등)

---

## GUI 사용법

### 1. 채널 설정
- 좌측 패널에서 각 채널(CH0-CH7)을 활성화
- **ON** 토글 스위치 클릭
- 레인지 선택: ±10V, ±5V, ±2.5V, ±1.25V, 0-10V, 0-5V 등

### 2. 모니터링 시작
- 상단 **Start** 버튼 클릭
- **ADC 연결 시**: 실시간 데이터 수집 시작
- **ADC 미연결 시**:
  - 시뮬레이션 모드 선택 대화상자 표시
  - "예" 선택 시 사인파 시뮬레이션 데이터 생성
  - "아니오" 선택 시 모니터링 취소
- 차트에 데이터 표시
- **Interval**: 측정 주기 설정 (0.1~10.0초)

### 시뮬레이션 모드 특징
- 채널별로 다른 주파수의 사인파 생성 (0.5Hz ~ 1.2Hz)
- ±5V 진폭의 신호에 노이즈 추가
- 모든 GUI 기능 테스트 가능 (차트, 통계, 저장 등)
- 하드웨어 없이 소프트웨어 개발 및 테스트 가능

### 3. 차트 제어
- **Y-Scale**:
  - Auto mode: 자동 범위 조정
  - ±10V Full, ±5V Full: 프리셋 (값 수정 가능)
  - Custom: 완전 수동 입력
  - 모든 모드에서 Y-Min/Y-Max 값 직접 수정 가능
  - Enter 키로 빠른 적용
- **Enable Cursor**: 측정 커서 활성화
- **Channel Display**: 표시할 채널 선택/해제 (체크박스)
- **Save Snapshot**: 차트를 이미지로 저장 (PNG/PDF)

### 4. 통계 확인
- 우측 패널 **Statistics** 섹션
- 채널 선택 후 통계 확인:
  - **RMS**: Root Mean Square
  - **Max**: 최대값
  - **Min**: 최소값
  - **Avg**: 평균값
  - **P-P**: Peak-to-Peak

### 5. Digital I/O 제어 ✨ (Control 패널 → Digital I/O 탭)
- **Digital Output**:
  - GPIO 23, 24 제어
  - [ON] [OFF] 버튼으로 간편 제어
  - 실시간 상태 표시 (HIGH/LOW, 색상 변경)
- **Digital Input**:
  - GPIO 13 모니터링
  - [Start Monitoring] / [Stop Monitoring]
  - 상태 표시: HIGH/LOW
- **Event Log**:
  - 입력 이벤트 자동 기록
  - 타임스탬프, GPIO 핀, 엣지 타입, 상태 표시
  - [Clear Log] 버튼으로 로그 삭제

### 6. 데이터 저장
- **Save Data**: CSV 파일로 데이터 저장
- **Save Config**: 현재 설정을 JSON으로 저장
- **Load**: 저장된 설정 불러오기
- **Save Snapshot**: 차트를 이미지로 저장 (PNG/PDF)

---

## 문제 해결

### Import 오류
```
ImportError: No module named 'ttkbootstrap'
```
**해결**: 가상 환경이 활성화되어 있는지 확인하세요:
```bash
source venv/bin/activate
pip3 install -r requirements.txt
```

### 패키지 설치 오류 (externally-managed-environment)
```
error: externally-managed-environment
```
**해결**: 가상 환경을 사용하세요:
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
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

### Permission 오류 (SPI/GPIO)
```
PermissionError: [Errno 13] Permission denied: '/dev/spidev0.0'
PermissionError: [Errno 13] Permission denied: '/dev/gpiochip0'
```
**해결**: 사용자를 필요한 그룹에 추가하세요:
```bash
# SPI 및 GPIO 그룹 추가
sudo usermod -a -G spi,gpio $USER

# 시스템 재부팅 또는 재로그인 필요
sudo reboot
```

**또는 가상 환경에서 sudo로 실행**:
```bash
# 가상 환경 경로를 직접 지정하여 실행
sudo /home/shinho/shinho/wdaq/venv/bin/python main.py
```

> **참고**: `gpiod` 라이브러리는 `/dev/gpiochip0` 디바이스에 접근하므로 `gpio` 그룹 권한이 필요합니다.

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
- **gpio_monitor.py**: GPIO 입력 모니터링
  - gpiod 기반 GPIO 이벤트 감지
  - 멀티 핀 동시 모니터링 (5, 13, 17, 22, 27)
  - Rising/Falling 엣지 감지
  - 이벤트 카운터 및 통계
- **gpio_controller.py**: GPIO 출력 제어
  - GPIO 23, 24 디지털 출력 제어
  - GPIO 13 입력 모니터링
  - gpiod 기반 안정적인 제어

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
  - control_panel.py: 탭 기반 컨트롤 (Statistics/GPIO/Digital I/O)
  - digital_io_panel.py: 디지털 입출력 제어 패널
  - status_bar.py: 상태바
- **widgets/**: 재사용 가능한 UI 컴포넌트
  - channel_widget.py: 개별 채널 위젯
  - chart_widget.py: 차트 위젯
  - gpio_widget.py: GPIO 상태/제어 위젯

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

## 레이아웃 구조

```
┌──────────────────────────────────────────────────────────────────┐
│  Header Panel (Start/Stop, Config, Interval)                    │
├──────────────┬──────────────────────────┬────────────────────────┤
│              │                          │ [Statistics] [GPIO]    │
│              │                          │ [Digital I/O] ✨       │
│  Channel     │      Chart Panel         ├────────────────────────┤
│  Panel       │      (Time Domain)       │ [Statistics Tab]       │
│  (8 Ch)      │                          │ - Y-Scale Control      │
│              │                          │ - Chart Tools          │
│              │                          │ - Channel Display      │
│  CH0-CH7     │   600px (Fixed Width)    │ - Statistics Info      │
│              │                          ├────────────────────────┤
│              │                          │ [GPIO Tab]             │
│              │                          │ - GPIO Input Status    │
│              │                          │ - GPIO Output Control  │
│              │                          │ - Alarm Status         │
│              │                          ├────────────────────────┤
│              │                          │ [Digital I/O Tab] ✨   │
│              │                          │ - GPIO 23, 24 Output   │
│              │                          │ - GPIO 13 Input        │
│              │                          │ - Event Log            │
└──────────────┴──────────────────────────┴────────────────────────┘
│  Status Bar (Time, Messages, Sample Rate)                        │
└──────────────────────────────────────────────────────────────────┘
```

## 버전 정보

- **Version**: 2.4
- **From**: gui_wdaq3.py (900줄 단일 파일)
- **To**: 30+ 모듈 (4,000+ 줄)
- **Latest Update**: 2025-12-10
  - 가상 환경 지원 추가 (venv)
  - ttkbootstrap API 호환성 수정 (LabelFrame → Labelframe)
  - gpiod 라이브러리 추가 (최신 GPIO 제어)
  - 실행 스크립트 개선 (run.sh)
  - Raspberry Pi OS Bookworm 완벽 지원
  - **시뮬레이션 모드 추가** (하드웨어 없이 GUI 테스트 가능)
  - 사인파 + 노이즈 시뮬레이션 데이터 생성
- **Previous**: 2025-10-24
  - Digital I/O 제어 패널 추가 (GPIO 23, 24, 13)
  - 차트 크기 최적화 (600px 고정)
  - Control Panel 탭 구조 개선 (Statistics/GPIO/Digital I/O)
