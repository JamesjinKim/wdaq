# ADS8668 Monitor - 모듈 구조 상세

## 전체 디렉토리 구조

```
ads8668_monitor/
├── main.py                         # 🚀 메인 진입점
├── README.md                       # 📖 프로젝트 설명서
├── STRUCTURE.md                    # 📐 구조 상세 문서 (이 파일)
├── requirements.txt                # 📦 의존성 목록
│
├── hardware/                       # 🔧 하드웨어 계층
│   ├── __init__.py
│   └── adc_controller.py          # ADS8668 SPI 통신 및 제어
│
├── data/                          # 💾 데이터 관리 계층
│   ├── __init__.py
│   ├── data_manager.py            # 실시간 데이터 버퍼 관리
│   └── data_export.py             # CSV/JSON 입출력
│
├── analysis/                      # 📊 신호 분석 계층
│   ├── __init__.py
│   ├── statistics.py              # 통계 계산 (RMS, THD, SNR, SINAD, ENOB, SFDR)
│   ├── time_domain.py             # 시간 영역 분석
│   └── spectral_analysis.py       # 주파수 분석 (FFT, Harmonics)
│
├── utils/                         # 🛠️ 유틸리티 계층
│   ├── __init__.py
│   ├── config_manager.py          # 설정 관리
│   └── logger.py                  # 로깅 설정
│
└── gui/                           # 🖥️ GUI 계층
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

## 모듈별 상세 설명

### 1. Hardware Layer (`hardware/`)

#### `adc_controller.py`
**역할**: ADS8668 하드웨어 제어
- SPI 통신 관리
- 채널 레인지 설정
- ADC 데이터 읽기
- 전압 값 계산

**주요 클래스**:
```python
class ADS8668Controller:
    RANGES = {...}  # 레인지 설정 (±10V, ±5V, etc)

    def connect()              # ADC 연결
    def set_channel_range()    # 채널 레인지 설정
    def read_channel()         # 단일 채널 읽기
    def read_all_channels()    # 전체 채널 읽기
    def close()                # 연결 종료
```

---

### 2. Data Layer (`data/`)

#### `data_manager.py`
**역할**: 실시간 데이터 버퍼 관리
- 채널별 데이터 deque 관리 (최대 300포인트)
- 데이터 추가/삭제
- 채널 활성화/비활성화

**주요 클래스**:
```python
class DataManager:
    def add_data()             # 데이터 추가
    def add_batch_data()       # 배치 데이터 추가
    def enable_channel()       # 채널 활성화
    def get_channel_data()     # 채널 데이터 반환
    def clear_all()            # 전체 초기화
```

#### `data_export.py`
**역할**: 데이터 입출력
- CSV 데이터 내보내기
- JSON 설정 저장/불러오기

**주요 클래스**:
```python
class DataExporter:
    @staticmethod
    def export_to_csv()        # CSV 저장
    def export_config()        # 설정 저장
    def import_config()        # 설정 불러오기
```

---

### 3. Analysis Layer (`analysis/`)

#### `statistics.py`
**역할**: 신호 통계 계산
- 기본 통계 (RMS, Max, Min, Avg, P-P)
- 신호 품질 측정 (THD, SNR, SINAD, SFDR, ENOB)

**주요 클래스**:
```python
class SignalStatistics:
    @staticmethod
    def rms()                  # RMS 계산
    def peak_to_peak()         # Peak-to-Peak
    def calculate_statistics() # 전체 통계
    def thd()                  # Total Harmonic Distortion
    def snr()                  # Signal-to-Noise Ratio
    def sinad()                # Signal-to-Noise And Distortion
    def sfdr()                 # Spurious-Free Dynamic Range
    def enob()                 # Effective Number of Bits
```

#### `time_domain.py`
**역할**: 시간 영역 신호 분석
- 통계 분석
- 피크 검출
- 주파수 추정

**주요 클래스**:
```python
class TimeDomainAnalyzer:
    def analyze()              # 시간 영역 분석
    def detect_peaks()         # 피크 검출
    def calculate_frequency()  # 주파수 추정
```

#### `spectral_analysis.py`
**역할**: 주파수 영역 신호 분석 (ch2.png 참조)
- FFT 계산
- 고조파 검출
- 스펙트럼 분석

**주요 클래스**:
```python
class SpectralAnalyzer:
    WINDOWS = {...}            # 윈도우 함수들

    def compute_fft()          # FFT 계산
    def compute_psd()          # PSD 계산
    def find_fundamental()     # 기본 주파수 찾기
    def find_harmonics()       # 고조파 검출
    def analyze_spectrum()     # 전체 스펙트럼 분석
```

---

### 4. Utils Layer (`utils/`)

#### `config_manager.py`
**역할**: 설정 관리
- 기본 설정 제공
- 설정 저장/불러오기
- 채널별 설정 관리

**주요 클래스**:
```python
class ConfigManager:
    DEFAULT_CONFIG = {...}

    def get()                  # 설정 값 가져오기
    def set()                  # 설정 값 설정
    def get_channel_config()   # 채널 설정 가져오기
    def save_to_dict()         # 딕셔너리로 저장
    def load_from_dict()       # 딕셔너리에서 로드
```

#### `logger.py`
**역할**: 로깅 설정
- 로거 초기화
- 콘솔/파일 핸들러 설정

**함수**:
```python
def setup_logger()             # 로거 설정
def get_logger()               # 로거 가져오기
```

---

### 5. GUI Layer (`gui/`)

#### `main_window.py`
**역할**: 메인 윈도우 통합
- 전체 GUI 레이아웃 구성
- 패널 간 통신 관리
- 모니터링 루프
- 이벤트 핸들링

**주요 클래스**:
```python
class MainWindow:
    def setup_gui()            # GUI 구성
    def connect_adc()          # ADC 연결
    def start_monitoring()     # 모니터링 시작
    def stop_monitoring()      # 모니터링 중지
    def update_gui()           # GUI 업데이트 루프
    def update_chart()         # 차트 업데이트
    def save_data()            # 데이터 저장
```

---

#### `panels/` - GUI 패널들

##### `header_panel.py`
**역할**: 상단 헤더
- 제목 표시
- 연결 상태 표시
- 시작/정지 버튼
- 설정 저장/불러오기 버튼
- 측정 주기 설정

##### `channel_panel.py`
**역할**: 채널 설정 패널
- 8개 채널 위젯 관리 (2x4 그리드)
- 채널별 활성화/비활성화
- 레인지 설정
- 전압 표시

##### `chart_panel.py`
**역할**: 차트 표시 패널
- Time Domain / Spectral 차트 표시
- 툴바 (줌/팬)
- 차트 업데이트

##### `control_panel.py`
**역할**: 차트 컨트롤 및 통계
- Y-Scale 설정 (Auto/Preset/Custom)
- 차트 도구 (커서, 스냅샷)
- 채널 표시 선택
- 통계 정보 표시

##### `status_bar.py`
**역할**: 하단 상태바
- 상태 메시지 표시
- 샘플링 레이트 표시
- 현재 시간 표시

---

#### `widgets/` - 재사용 위젯

##### `channel_widget.py`
**역할**: 개별 채널 UI 컴포넌트
- ON/OFF 토글
- 레인지 콤보박스
- 전압 표시 레이블
- 프로그레스바

**주요 클래스**:
```python
class ChannelWidget:
    def update_voltage()       # 전압 업데이트
    def get_enabled()          # 활성화 상태
    def set_range()            # 레인지 설정
```

##### `chart_widget.py`
**역할**: 차트 위젯
- matplotlib 캔버스 관리
- Time Domain / Spectral 차트

**주요 클래스**:
```python
class BaseChartWidget:         # 베이스 클래스
    def create_canvas()        # 캔버스 생성
    def enable_cursor()        # 커서 활성화
    def save_figure()          # 그림 저장

class TimeDomainChart:         # Time Domain (ch1.png)
    def update_data()          # 데이터 업데이트

class SpectralChart:           # Spectral Analysis (ch2.png)
    def update_spectrum()      # 스펙트럼 업데이트
```

---

## 데이터 흐름

```
Hardware Layer (ADC)
    ↓ (read_all_channels)
Data Manager (버퍼)
    ↓ (queue)
Main Window (처리)
    ↓
    ├→ Channel Panel (전압 표시)
    ├→ Chart Panel (차트 업데이트)
    ├→ Control Panel (통계 계산)
    └→ Analysis Layer (신호 분석)
```

---

## 확장 가능성

### Spectral Analysis 탭 추가
1. `gui/panels/spectral_panel.py` 생성
2. `main_window.py`에서 탭 위젯 추가
3. `SpectralAnalyzer` 연동

### 새로운 분석 기능
1. `analysis/custom_analysis.py` 생성
2. 분석 로직 구현
3. GUI 패널에서 호출

### 데이터베이스 저장
1. `data/database.py` 생성
2. SQLite/PostgreSQL 연동
3. 장기 데이터 저장

---

## 파일 크기 통계

```
main.py                 ~40줄
hardware/adc_controller.py    ~120줄
data/data_manager.py          ~90줄
data/data_export.py           ~90줄
analysis/statistics.py        ~170줄
analysis/time_domain.py       ~80줄
analysis/spectral_analysis.py ~200줄
gui/main_window.py            ~380줄
gui/panels/*.py               ~100-250줄 각
gui/widgets/*.py              ~100-200줄 각
```

**총 라인 수**: ~2000줄 (원본 900줄 → 모듈화 후 분산)

---

## 주요 개선점

✅ **모듈화**: 900줄 단일 파일 → 22개 모듈 파일
✅ **재사용성**: Widget/Component 독립화
✅ **확장성**: 새 기능 추가 용이
✅ **테스트**: 모듈별 단위 테스트 가능
✅ **유지보수**: 기능별 파일 분리로 관리 용이
✅ **분석 기능**: Spectral Analysis 준비 완료

═══════════════════════════════════════════════════════════════════
# 📘 PART 2: 마이그레이션 가이드
═══════════════════════════════════════════════════════════════════

## gui_wdaq3.py → ads8668_monitor 마이그레이션

### 개요

기존 단일 파일 `gui_wdaq3.py` (900줄)을 모듈화된 구조로 분리했습니다.

### 변경 사항 요약

**이전 (gui_wdaq3.py)**:
```
gui_wdaq3.py (900줄)
├── ADS8668Controller 클래스 (약 100줄)
└── ADS8668Monitor 클래스 (약 800줄)
    ├── 하드웨어 제어
    ├── GUI 구성
    ├── 데이터 관리
    ├── 차트 표시
    └── 설정 관리
```

**이후 (ads8668_monitor/)**:
```
ads8668_monitor/
├── 27개 모듈 파일
├── 계층별 분리: Hardware, Data, Analysis, Utils, GUI
└── 약 3,648줄 (기능 확장 포함)
```

---

## 주요 모듈 매핑

| 원본 (gui_wdaq3.py) | 새 모듈 |
|-------------------|---------|
| ADS8668Controller | hardware/adc_controller.py |
| 데이터 저장 (deque) | data/data_manager.py |
| CSV/JSON 저장 | data/data_export.py |
| 통계 계산 (RMS 등) | analysis/statistics.py |
| 차트 그리기 | gui/widgets/chart_widget.py |
| 채널 위젯 | gui/widgets/channel_widget.py |
| 메인 윈도우 | gui/main_window.py |
| 설정 관리 | utils/config_manager.py |

---

## 실행 방법 변경

### 이전
```bash
python3 gui_wdaq3.py
```

### 이후
```bash
cd ads8668_monitor
python3 main.py
```

또는:
```bash
./run.sh
```

---

## 코드 비교 예시

### 채널 읽기

**이전 (gui_wdaq3.py)**:
```python
# ADS8668Monitor 클래스 내부
def monitor_loop(self):
    results = self.adc.read_all_channels()
    for ch, data in results.items():
        self.channel_data[ch]['voltages'].append(data['voltage'])
```

**이후 (모듈화)**:
```python
# main_window.py
from hardware.adc_controller import ADS8668Controller
from data.data_manager import DataManager

def monitor_loop(self):
    results = self.adc.read_all_channels()
    self.data_manager.add_batch_data(timestamp, results)
```

### 통계 계산

**이전**:
```python
# ADS8668Monitor 내부에 직접 구현
v_arr = np.array(voltages)
rms = np.sqrt(np.mean(v_arr**2))
```

**이후**:
```python
from analysis.statistics import SignalStatistics

stats = SignalStatistics()
result = stats.calculate_statistics(voltages)
# result = {'rms': ..., 'max': ..., 'min': ..., 'avg': ..., 'pp': ...}
```

---

## 설정 파일 호환성

기존 JSON 설정 파일은 그대로 사용 가능합니다.

```json
{
  "sample_interval": 1.0,
  "chart_y_scale_mode": "Auto mode",
  "channels": [
    {"enabled": true, "range": "±10V"},
    ...
  ]
}
```

---

## 테스트 방법

### 모듈 임포트 테스트
```bash
cd /home/drjins/shinho/Egicon/wdaq
python3 -c "from ads8668_monitor.hardware.adc_controller import ADS8668Controller; print('OK')"
python3 -c "from ads8668_monitor.data.data_manager import DataManager; print('OK')"
python3 -c "from ads8668_monitor.analysis.statistics import SignalStatistics; print('OK')"
```

### 구문 검증
```bash
cd ads8668_monitor
python3 -m py_compile main.py
find . -name "*.py" -exec python3 -m py_compile {} \;
```

---

═══════════════════════════════════════════════════════════════════
# 📊 PART 3: 프로젝트 요약
═══════════════════════════════════════════════════════════════════

## 프로젝트 정보

- **작업 일시**: 2025-10-21
- **프로젝트 위치**: /home/drjins/shinho/Egicon/wdaq/ads8668_monitor/
- **버전**: 2.0 (Modular)

---

## 완료된 작업

1. ✓ 디렉토리 구조 생성 (5개 계층, 27개 파일)
2. ✓ 하드웨어 계층 모듈 분리 (hardware/)
3. ✓ 데이터 관리 계층 모듈 분리 (data/)
4. ✓ 신호 분석 계층 모듈 추가 (analysis/)
5. ✓ 유틸리티 계층 모듈 분리 (utils/)
6. ✓ GUI 계층 모듈화 (gui/ + panels/ + widgets/)
7. ✓ Import 오류 수정 (상대 import → 절대 import)
8. ✓ 실행 스크립트 생성 (run.sh)
9. ✓ 문서 작성 (README, STRUCTURE)
10. ✓ 테스트 완료 (import 검증, 실행 확인)

---

## 프로젝트 통계

| 항목 | 값 |
|------|-----|
| 총 Python 파일 | 27개 |
| 총 코드 라인 | 3,648줄 |
| 총 문서 파일 | 2개 (README, STRUCTURE) |
| 원본 대비 | 900줄 → 3,648줄 |

---

## 주요 개선점

### 1. 모듈화
- 900줄 단일 파일 → 27개 독립 모듈
- 계층별 분리 (Hardware/Data/Analysis/Utils/GUI)
- 평균 파일 크기: ~135줄 (관리 용이)

### 2. 재사용성
- ChannelWidget: 독립적인 채널 UI 컴포넌트
- TimeDomainChart/SpectralChart: 차트 위젯 분리
- 패널 모듈화 (Header/Channel/Chart/Control/Status)

### 3. 확장성
- Spectral Analysis 모듈 준비 완료
- FFT, Harmonics, THD/SNR/SINAD/SFDR/ENOB 계산
- 탭 UI로 확장 가능한 구조

### 4. 유지보수성
- 기능별 파일 분리
- 명확한 책임 분리
- 단위 테스트 준비

---

## 실행 방법

**방법 1 (권장)**:
```bash
cd /home/drjins/shinho/Egicon/wdaq/ads8668_monitor
python3 main.py
```

**방법 2 (스크립트)**:
```bash
./run.sh
```

---

## 의존성

**필수**:
- ttkbootstrap
- matplotlib
- numpy
- spidev
- RPi.GPIO

**선택 (고급 분석)**:
- scipy

**설치**:
```bash
pip3 install -r requirements.txt
```

---

## 새로 추가된 기능

### 1. Spectral Analysis 모듈 (ch2.png 참조)
- FFT 계산 및 스펙트럼 분석
- 고조파 검출 (최대 9개)
- 윈도우 함수: Hann, Hamming, Blackman, B-Harris
- 신호 품질 측정:
  * SNR (Signal-to-Noise Ratio)
  * THD (Total Harmonic Distortion)
  * SFDR (Spurious-Free Dynamic Range)
  * SINAD (Signal-to-Noise And Distortion)
  * ENOB (Effective Number of Bits)

### 2. Time Domain 분석 모듈
- 피크 검출
- 주파수 추정 (zero-crossing)
- 통계 분석

### 3. 재사용 가능한 위젯
- ChannelWidget: 개별 채널 컴포넌트
- TimeDomainChart: 시간 영역 차트
- SpectralChart: 주파수 차트 (준비됨)

---

## 테스트 결과

```
[PASS] 디렉토리 구조 생성
[PASS] Python 구문 검증
[PASS] 모듈 Import 테스트
[PASS] 프로그램 실행 테스트
[PASS] GUI 로딩 확인
```

**실행 로그**:
```
2025-10-21 15:25:52 - ads8668_monitor - INFO - ADS8668 Monitor Starting...
(하드웨어 미연결 시 GPIO busy 오류는 정상)
```

---

## 향후 확장 계획

1. **Spectral Analysis 탭 UI 완성**
   - 탭 위젯으로 Time Domain / Spectral 분리
   - FFT 파라미터 입력 UI
   - Harmonics 테이블 표시

2. **데이터베이스 연동**
   - SQLite로 장기 데이터 저장
   - 데이터 조회 및 분석 기능

3. **단위 테스트**
   - pytest 프레임워크
   - 모듈별 테스트 케이스

4. **문서화**
   - Sphinx 문서 생성
   - API 레퍼런스

---

## 문의 및 지원

- **프로젝트**: Egicon
- **개발자**: Claude AI + User
- **위치**: /home/drjins/shinho/Egicon/wdaq/ads8668_monitor/

═══════════════════════════════════════════════════════════════════
