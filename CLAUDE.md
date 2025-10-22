# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ADS8668 ADC Monitor - An 8-channel ADC monitoring application for the ADS8668 chip. The project is structured as a modular Python application with layers for hardware control, data management, signal analysis, and GUI.

**Key Facts:**
- Migrated from 900-line monolithic file to 27 modular files
- Runs on Raspberry Pi with SPI hardware
- GUI built with ttkbootstrap (modern tkinter theme)
- Real-time monitoring with matplotlib charts
- Supports both time-domain and spectral analysis

## Development Commands

### Running the Application
```bash
# Primary method
python3 main.py

# Alternative (using shell script if present)
./run.sh
```

### Installing Dependencies
```bash
# Install all required packages
pip3 install -r requirements.txt

# Individual packages
pip3 install ttkbootstrap matplotlib numpy scipy spidev RPi.GPIO
```

### Testing Module Imports
```bash
# Verify individual module imports
python3 -c "from hardware.adc_controller import ADS8668Controller; print('OK')"
python3 -c "from data.data_manager import DataManager; print('OK')"
python3 -c "from analysis.statistics import SignalStatistics; print('OK')"

# Compile all Python files
find . -name "*.py" -exec python3 -m py_compile {} \;
```

## Architecture

### Layer Structure

The codebase follows a strict layered architecture:

```
Hardware Layer (hardware/)
    ↓ SPI communication
Data Layer (data/)
    ↓ buffering and export
GUI Layer (gui/)
    ↓ uses
Analysis Layer (analysis/)
    ↓ uses
Utils Layer (utils/)
```

### Hardware Layer (`hardware/`)

**`adc_controller.py`** - ADS8668 SPI communication and control
- Class: `ADS8668Controller`
- Key methods: `connect()`, `read_channel()`, `read_all_channels()`, `set_channel_range()`
- Manages SPI communication using spidev and RPi.GPIO
- Channel ranges defined in `RANGES` dict (±10V, ±5V, ±2.5V, etc.)
- CS pin control via GPIO BCM pin 8

### Data Layer (`data/`)

**`data_manager.py`** - Real-time data buffer management
- Class: `DataManager`
- Uses `collections.deque` with max 300 points per channel
- Thread-safe data queuing for GUI updates

**`data_export.py`** - File I/O for CSV and JSON
- Class: `DataExporter`
- Static methods for CSV export, config save/load

### Analysis Layer (`analysis/`)

**`statistics.py`** - Signal statistics
- Class: `SignalStatistics`
- Computes: RMS, Max, Min, Avg, Peak-to-Peak
- Advanced metrics: THD, SNR, SINAD, SFDR, ENOB

**`spectral_analysis.py`** - FFT and frequency domain analysis
- Class: `SpectralAnalyzer`
- Supports window functions: Hann, Hamming, Blackman, Blackman-Harris
- Harmonic detection (up to 9 harmonics)

**`time_domain.py`** - Time-domain signal analysis
- Class: `TimeDomainAnalyzer`
- Peak detection, frequency estimation

### GUI Layer (`gui/`)

**`main_window.py`** - Main application controller
- Class: `MainWindow`
- Orchestrates all panels and manages application state
- Runs monitoring in separate thread with `threading.Thread`
- GUI updates via `root.after()` callback every 500ms
- Uses `queue.Queue` for thread-safe data passing

**Panels** (`gui/panels/`)
- `header_panel.py` - Top header with start/stop, save/load buttons
- `channel_panel.py` - 8-channel grid (2x4) with ON/OFF toggles
- `chart_panel.py` - matplotlib chart container
- `control_panel.py` - Y-scale controls, cursor toggle, statistics display
- `status_bar.py` - Bottom status messages and time display

**Widgets** (`gui/widgets/`)
- `channel_widget.py` - Individual channel UI component (toggle, range selector, voltage display)
- `chart_widget.py` - Base chart widget with `TimeDomainChart` and `SpectralChart` classes

### Utils Layer (`utils/`)

**`config_manager.py`** - Configuration management
- Class: `ConfigManager`
- Stores default config in `DEFAULT_CONFIG` dict

**`logger.py`** - Logging setup
- Functions: `setup_logger()`, `get_logger()`
- Configured for INFO level by default

## Key Design Patterns

### Threading Model
- Main thread runs tkinter GUI event loop
- Monitoring thread (daemon) reads ADC data at configured interval
- Data passed to main thread via `queue.Queue`
- GUI updates in main thread using `root.after(500, update_gui)`

### Configuration Flow
1. User changes settings in GUI panels
2. Callbacks update `MainWindow` state
3. State reflected in `ConfigManager` and `DataManager`
4. Save/load via `DataExporter` to/from JSON

### Data Flow
```
ADS8668Controller.read_all_channels()
  → data_queue.put() [monitoring thread]
  → data_manager.add_batch_data() [main thread]
  → channel_panel.update_channel_display()
  → chart_panel.update_time_domain()
  → control_panel.update_statistics()
```

### Panel Communication
All panels communicate through `MainWindow` using callback functions passed during initialization. Panels do not directly call each other.

## Hardware-Specific Considerations

### Raspberry Pi Dependencies
- `RPi.GPIO` - Only works on Raspberry Pi hardware
- `spidev` - Requires `/dev/spidev0.0` device
- SPI must be enabled via `raspi-config`

### Mock/Development Mode
The application attempts hardware connection but continues if it fails. When developing without hardware:
- ADC connection fails but GUI still loads
- "GPIO busy" or "Not running on a RPi" errors are normal
- All GUI features work except actual data acquisition

### SPI Communication
- Uses SPI mode 1 (CPOL=0, CPHA=1)
- Max speed: 10 MHz
- Chip select controlled manually via GPIO pin 8
- 4-byte transfers for reading channels

## Important Conventions

### Import Style
All imports use absolute imports from package root:
```python
from hardware.adc_controller import ADS8668Controller
from data.data_manager import DataManager
```

Never use relative imports (`from .hardware import ...`)

### Channel Indexing
- Channels numbered 0-7 (not 1-8)
- All arrays/dicts use 0-based indexing

### Range Configuration
Ranges stored as dict with keys 0-8, each containing:
- `name`: String like "±10V" or "0-5V"
- `reg`: Register value for ADS8668
- `offset`: Hex offset (0x800 for bipolar, 0x000 for unipolar)
- `scale`: Voltage scale factor

### Logging
Use module-level logger:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("message")
```

## Common Tasks

### Adding a New Analysis Function
1. Create new method in appropriate class in `analysis/`
2. Add UI controls in relevant panel (`control_panel.py`)
3. Call from `MainWindow.update_statistics()` or create new update method
4. Update callback chain in `setup_gui()`

### Adding a New Panel
1. Create panel class in `gui/panels/`
2. Inherit pattern from existing panels (take parent and callbacks dict)
3. Instantiate in `MainWindow.setup_gui()`
4. Pack into appropriate frame (left/center/right)
5. Add callbacks to MainWindow for panel events

### Modifying Channel Configuration
1. Update `ADS8668Controller.RANGES` dict if adding new range
2. Update range dropdown in `channel_widget.py`
3. Update `set_channel_range()` logic if needed

### Extending Spectral Analysis UI
The spectral analysis backend is complete but not integrated into GUI:
1. Add tab widget in `chart_panel.py` or create `spectral_panel.py`
2. Use `SpectralChart` from `chart_widget.py`
3. Call `SpectralAnalyzer.analyze_spectrum()` with buffered data
4. Display harmonics table and metrics in control panel

## File Locations

- Entry point: [main.py](main.py)
- Hardware control: [hardware/adc_controller.py](hardware/adc_controller.py)
- Main app logic: [gui/main_window.py](gui/main_window.py)
- Data buffering: [data/data_manager.py](data/data_manager.py)
- Signal stats: [analysis/statistics.py](analysis/statistics.py)
- FFT analysis: [analysis/spectral_analysis.py](analysis/spectral_analysis.py)

## Troubleshooting

### Import Errors
- Ensure you're running from the parent directory of `ads8668_monitor/`
- All imports assume package is importable (not running from within package)

### Hardware Connection Issues
- Check SPI enabled: `ls /dev/spidev*`
- Verify GPIO permissions: `sudo usermod -a -G spi,gpio $USER`
- May need `sudo python3 main.py` for GPIO access

### GUI Performance
- Chart updates every 500ms regardless of sample rate
- Deque limited to 300 points to prevent memory growth
- If sluggish, reduce sample rate or increase update interval

### Threading Issues
- Never call tkinter methods from monitoring thread
- Always use `data_queue.put()` to pass data to main thread
- GUI updates only in main thread via `root.after()`


#중요사항-항상 한국어로 답변 할 것!