# Home Assistant Button Controller 🔘

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)
[![GitHub Release](https://img.shields.io/github/release/[JoJuStudio]/home-assistant-button-controller.svg)](https://github.com/[yourusername]/home-assistant-button-controller/releases)

A secure Python utility for controlling Home Assistant buttons via REST API with system keyring integration.

**Key Features**:
- 🔒 Encrypted credential storage using native system keyrings
- 🔄 Multi-button configuration management
- 🌐 Network timeout and SSL verification handling
- 📋 Connection testing and validation
- 📦 Cross-platform support (Linux/macOS/Windows)

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites
- Python 3.7+
- Home Assistant instance (v2021.3+)
- Valid API token with `button:write` permissions

### Steps
```bash
# Clone repository
git clone https://github.com/[yourusername]/home-assistant-button-controller.git
cd home-assistant-button-controller

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Initial Setup**
   ```bash
   python3 ha_button_controller.py --setup
   ```
   Follow prompts to enter:
   - Home Assistant URL (e.g., `https://homeassistant.local:8123`)
   - API token (created in Home Assistant Profile → Long-Lived Access Tokens)

2. **Add Buttons**
   ```bash
   # Example: Add office PC wake button
   Button label: office_pc
   Entity ID: button.office_pc_wake
   ```

## Usage

```bash
# Press a configured button
python3 ha_button_controller.py --press office_pc

# List configured buttons
python3 ha_button_controller.py --list

# Test HA connection
python3 ha_button_controller.py --verify

# Show help
python3 ha_button_controller.py --help
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SSL Certificate Errors | `export REQUESTS_CA_BUNDLE=/path/to/cert.pem` |
| Keyring Locked | Unlock through system keyring manager |
| API Connection Failed | Verify URL/token and firewall rules |
| Missing Buttons | Check entity exists in Home Assistant |

**Windows Keyring Setup**:
```powershell
pip install keyrings.alt
$env:PYTHON_KEYRING_BACKEND="keyring.backends.Windows.WinVaultKeyring"
```

## Development

### Contribution Guidelines
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

### Testing
```bash
# Run test suite
pytest tests/

# Generate coverage report
pytest --cov=src --cov-report=html
```

## License

Copyright (C) [2025] [John Jung]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or any later version.

**Full License Text**: [LICENSE](LICENSE)

## Acknowledgments
- Home Assistant REST API
- Python Keyring Library Team
- SecretStorage contributors

---

**Legal Disclaimer**: Dieses Programm wird ohne jegliche Gewährleistung bereitgestellt. Die Haftung für Schäden ist ausgeschlossen, soweit nicht Vorsatz oder grobe Fahrlässigkeit vorliegt (§§ 536a, 309 BGB).
