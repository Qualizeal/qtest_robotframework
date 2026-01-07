*** Settings ***
Documentation     Simple QTest Integration Example
...               Minimal example showing basic QTest integration
Library           ../../qtest_robot_library.py

*** Variables ***
${CONFIG_PATH}      ${EXECDIR}${/}config.json
${TEST_RUN_ID}      ${EMPTY}
${TEST_CASE_ID}     56168926
${PARENT_CYCLE_ID}    22801769
*** Test Cases ***
Simple Test With QTest Reporting
    [Documentation]    Simple test that reports to QTest
    [Tags]    simple    demo
    
    # Initialize QTest
    Initialize QTest Manager    ${CONFIG_PATH}
    
    # Create test run
    ${run_id}=    Create QTest Test Run
    ...    name=Simple Test Run
    ...    test_case_ids=56168926
    ...    test_cycle_id=${PARENT_CYCLE_ID}
    
    Set Test Variable    ${TEST_RUN_ID}    ${run_id}
    
    # Execute test logic
    Log    Executing test logic
    ${result}=    Set Variable    PASSED
    
    # Report result
    Report QTest Result
    ...    test_run_id=${TEST_RUN_ID}
    ...    test_case_id=${TEST_CASE_ID}
    ...    status=${result}
    ...    message=Test completed successfully
    ...    execution_time=1500
    
    # Finalize
    Finalize QTest Run
