# Changelog

## [1.1.0] - 2026-03-09

### Added
- **Real-time Progress Display**: Visual progress bar showing installation completion percentage
- **Step-by-Step Indicators**: Clear display of current installation step and total steps
- **Enhanced Logging**: Color-coded log messages (INFO, SUCCESS, WARNING, ERROR, PROGRESS)
- **Installation Header**: Beautiful formatted header showing environment name and version
- **Detailed Report**: Comprehensive installation summary with all relevant information

### Improved
- **Better Terminal Compatibility**: ASCII-friendly symbols instead of Unicode emojis
- **Real-time Output**: Package installation progress shown as it happens
- **User Experience**: Clear visual feedback throughout the installation process

### Technical Details
- Added `init_progress()`, `update_progress()`, `show_header()` functions
- Enhanced `log()` function with visual indicators
- Updated `install_v2ray.sh` and `install_lerobot.sh` to use new progress functions
- Improved error reporting and status tracking

## [1.0.0] - 2026-03-09

### Initial Release
- V2Ray installation automation
- LeRobot installation with PyTorch
- Environment detection and validation
- Automatic dependency installation
- CUDA/GPU support detection
- Virtual environment setup
- Installation logging
