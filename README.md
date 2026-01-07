# QTest Automation Project

This project provides automation scripts to interact with QTest API for:
- Creating test runs
- Updating test case results
- Managing test execution

## Prerequisites

- Python 3.7 or higher
- QTest account with API access
- QTest API token

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your QTest credentials in `config.json`:
```json
{
  "qtest_url": "https://your-domain.qtestnet.com",
  "api_token": "your-api-token-here",
  "project_id": 12345
}
```

## Usage

### Update Test Case Results
```python
from qtest_manager import QTestManager

manager = QTestManager()
manager.update_test_result(
    test_run_id=123,
    test_case_id=456,
    status="PASSED",
    note="Test executed successfully"
)
```

### Create Test Run
```python
manager.create_test_run(
    name="Automated Test Run",
    test_case_ids=[123, 456, 789],
    test_cycle_id=100
)
```

## Project Structure

- `qtest_manager.py` - Main QTest API manager
- `qtest_api.py` - QTest API wrapper
- `qtest_robot_library.py` - Robot Framework library
- `config.json` - Configuration file
- `examples/` - Example Python scripts
- `tests/robot/` - Robot Framework test files
- `utils/` - Utility functions

## Features

- ✅ Create test runs
- ✅ Update test case execution results
- ✅ Bulk update test results
- ✅ Error handling and logging
- ✅ Configurable via JSON
- ✅ Robot Framework integration
- ✅ Automated test result reporting

## License

MIT License
