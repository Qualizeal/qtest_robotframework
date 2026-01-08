*** Settings ***
Documentation     QTest Integration Test Suite
...               This suite demonstrates how to integrate QTest with Robot Framework tests
Library           Collections
Library           DateTime
Library           ../../qtest_robot_library.py

# Suite Setup       Setup QTest Integration
Suite Teardown    Finalize QTest Test Run
Test Setup        Run Keywords    Setup QTest Integration    AND    Log Test Start
Test Teardown     Report Test Result 

*** Variables ***
${QTEST_CONFIG}         ${EXECDIR}${/}config.json
${TEST_CYCLE_NAME}        TestDemo
${TEST_RUN_NAME}        Robot Framework Test Run -
@{TEST_CASE_NAME}        Sample Case 2

*** Test Cases ***
# Admin-Dashboard-Dashboard Client's Page
Sample Case 2
    [Documentation]    Test login functionality with valid credentials
    [Tags]    login    smoke    critical
    Log    Starting login test with valid credentials
    ${result}=    Simulate Login Test    valid_user    valid_password
    Should Be Equal    ${result}    success
    ${STEP_LOGS}=    Append QTest Test Step Log    ${TEST_CASE_ID}    ${STEP_LOGS}    1    PASSED    Actual ok    Expected ok    Step ran fine
    Log    Login test passed successfully
    ${STEP_LOGS}=    Append QTest Test Step Log    ${TEST_CASE_ID}    ${STEP_LOGS}    2    PASSED    Actual ok    Expected ok    Step ran fine

*** Keywords ***
Setup QTest Integration
    [Documentation]    Initialize QTest integration and create test run
    ${date}=    Get Current Date    result_format=%Y-%m-%d %H:%M
    Set Suite Variable    ${CURRENT_DATE}    ${date}
    
    Log    Initializing QTest Integration
    Initialize QTest Manager    ${QTEST_CONFIG}
    Log    Creating test run in QTest
    ${test_run_id}=    Create Qtest Test Run   
    ...    name=${TEST_RUN_NAME}  
    ...    test_case_name=${TEST_CASE_NAME}   
    ...    test_cycle_name=${TEST_CYCLE_NAME}
    
    Set Suite Variable    ${TEST_RUN_ID}    ${test_run_id}
    Log    Test Run Created - ID: ${test_run_id}
    # Resolve and store the current test's qTest case ID for reuse in this test
    ${test_case_id}=    Get QTest Test Case ID    ${TEST_NAME}
    Set Test Variable    ${TEST_CASE_ID}    ${test_case_id}
    Log    Test Case ID - ${TEST_CASE_ID}

Log Test Start
    [Documentation]    Log the start of each test
    Log    Starting test: ${TEST_NAME}
    ${logs}=    Create Dictionary
    Set Test Variable    ${STEP_LOGS}    ${logs}

Report Test Result
    [Documentation]    Report test result to QTest
    ${status}=    Get Test Status
    ${message}=    Get Test Message
    ${execution_time}=    Get Test Execution Time
    ${exe_start}=    Get Test Execution Start
    ${exe_end}=    Get Test Execution End
    
    Log    Reporting result to QTest: ${status}
    
    # ${test_case_id}=    Get QTest Test Case ID    ${TEST_NAME}
    
    Report QTest Result
    ...    test_run_id=${TEST_RUN_ID}
    ...    test_case_id=${TEST_CASE_ID}
    ...    status=${status}
    ...    steplogs=${STEP_LOGS}
    ...    message=${message}
    ...    execution_time=${execution_time}
    ...    exe_start_date=${exe_start}
    ...    exe_end_date=${exe_end}
    

Finalize QTest Test Run
    [Documentation]    Finalize and close QTest test run
    Log    Finalizing QTest test run
    Finalize QTest Run
    Log    QTest integration completed

# Test Simulation Keywords (Replace with actual test logic)
Simulate Login Test
    [Arguments]    ${username}    ${password}
    [Documentation]    Simulate login test logic
    Log    Attempting login with username: ${username}
    Sleep    1s
    Run Keyword If    '${username}' == 'valid_user'    Return From Keyword    success
    Return From Keyword    failure

Simulate Registration Test
    [Arguments]    ${user_data}
    [Documentation]    Simulate user registration test
    Log    Registering user: ${user_data}[username]
    Sleep    1.5s
    Return From Keyword    success

Simulate Dashboard Load
    [Documentation]    Simulate dashboard loading test
    Log    Loading dashboard
    Sleep    2s
    ${load_time}=    Evaluate    2.5
    Return From Keyword    ${load_time}

Simulate Search Test
    [Arguments]    ${query}
    [Documentation]    Simulate search functionality test
    Log    Searching for: ${query}
    Sleep    1s
    ${results}=    Evaluate    15
    Return From Keyword    ${results}

Get Test Status
    [Documentation]    Get current test status (PASSED/FAILED)
    ${status}=    Run Keyword And Return Status    Should Be True    True
    ${result}=    Set Variable If    ${status}    PASSED    FAILED
    Return From Keyword    ${result}

Get Test Message
    [Documentation]    Get test execution message
    ${message}=    Set Variable    Test executed via Robot Framework
    Return From Keyword    ${message}

Get Test Execution Time
    [Documentation]    Get test execution time in milliseconds
    # This would normally come from Robot Framework's built-in timing
    ${time_ms}=    Evaluate    3000
    Return From Keyword    ${time_ms}

Get Test Execution Start
    [Documentation]    Get test execution start timestamp (ISO 8601)
    ${start}=    Get Current Date    result_format=%Y-%m-%dT%H:%M:%S+00:00
    Return From Keyword    ${start}

Get Test Execution End
    [Documentation]    Get test execution end timestamp (ISO 8601)
    ${end}=    Get Current Date    result_format=%Y-%m-%dT%H:%M:%S+00:00
    Return From Keyword    ${end}

Get QTest Test Case ID
    [Arguments]    ${test_name}
    [Documentation]    Map Robot Framework test name to QTest test case ID
    ${test_case_id}=    Get QTest Test Case ID By Name    ${test_name}
    Return From Keyword    ${test_case_id}