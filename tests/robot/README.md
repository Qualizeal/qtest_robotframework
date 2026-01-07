# Robot Framework Integration with QTest

This directory contains Robot Framework test files that integrate with QTest for automated test result reporting.

## Setup

1. Install Robot Framework dependencies:
```powershell
pip install -r requirements-robot.txt
```

2. Configure QTest credentials in `config.json`

## Test Files

### 1. simple_qtest_test.robot
Basic example showing minimal QTest integration with a single test case.

**Run:**
```powershell
robot tests\robot\simple_qtest_test.robot
```

### 2. qtest_integration_tests.robot
Comprehensive test suite with multiple test cases and full QTest integration including:
- Suite setup/teardown with test run creation
- Automatic test result reporting
- Test case mapping
- Execution time tracking

**Run:**
```powershell
robot tests\robot\qtest_integration_tests.robot
```

### 3. advanced_qtest_tests.robot
Advanced features including:
- Dynamic test cycle creation
- Bulk test result updates
- Status verification
- Timer utilities

**Run:**
```powershell
robot tests\robot\advanced_qtest_tests.robot
```

## QTest Robot Library Keywords

### Setup Keywords
- `Initialize QTest Manager` - Initialize the QTest manager with configuration
- `Create QTest Test Run` - Create a new test run in QTest
- `Create QTest Test Cycle` - Create a new test cycle in QTest

### Execution Keywords
- `Report QTest Result` - Report individual test result to QTest
- `Bulk Report QTest Results` - Report multiple test results at once
- `Start Test Timer` - Start timing a test execution
- `Get Test Duration Ms` - Get test duration in milliseconds

### Utility Keywords
- `Get QTest Execution Statuses` - Get available execution statuses
- `Finalize QTest Run` - Finalize and cleanup test run

## Example Usage

```robot
*** Settings ***
Library    ../../qtest_robot_library.py

*** Test Cases ***
My Test Case
    Initialize QTest Manager    config.json
    ${run_id}=    Create QTest Test Run    name=My Run    test_case_ids=123,456
    
    # Your test logic here
    
    Report QTest Result    
    ...    test_run_id=${run_id}
    ...    test_case_id=123
    ...    status=PASSED
    ...    message=Test passed
    
    Finalize QTest Run
```

## Test Case Mapping

Update the `Get QTest Test Case ID` keyword in `qtest_integration_tests.robot` to map your Robot Framework test names to QTest test case IDs:

```robot
Get QTest Test Case ID
    [Arguments]    ${test_name}
    ${mapping}=    Create Dictionary
    ...    TC001_Login=12345
    ...    TC002_Register=12346
    ...    TC003_Search=12347
    
    ${test_case_id}=    Get From Dictionary    ${mapping}    ${test_name}
    Return From Keyword    ${test_case_id}
```

## Running All Tests

Run all Robot Framework tests:
```powershell
robot tests\robot\
```

Run with specific tags:
```powershell
robot --include smoke tests\robot\
robot --include qtest tests\robot\
```

Generate detailed reports:
```powershell
robot --outputdir results tests\robot\
```

## Troubleshooting

1. **Import Error**: Make sure the parent directory is in Python path
2. **Config Not Found**: Verify `config.json` path is correct
3. **QTest API Errors**: Check your API token and project ID in config
4. **Test Case ID Mismatch**: Update the test case mapping dictionary

## Best Practices

1. Always call `Initialize QTest Manager` in Suite Setup
2. Create test run once per suite (not per test)
3. Use `Finalize QTest Run` in Suite Teardown
4. Map Robot test names to QTest test case IDs clearly
5. Handle QTest reporting failures gracefully (don't fail tests due to reporting issues)
