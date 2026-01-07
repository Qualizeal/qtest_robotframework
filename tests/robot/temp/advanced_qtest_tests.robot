*** Settings ***
Documentation     Advanced QTest Integration with Robot Framework
...               Demonstrates advanced features including test cycles, bulk updates, and error handling
Library           ../../qtest_robot_library.py
Library           Collections
Library           String

Suite Setup       Advanced Setup
Suite Teardown    Advanced Teardown

*** Variables ***
${QTEST_CONFIG}         ../../config.json
${TEST_CYCLE_NAME}      Advanced Robot Test Cycle
${TEST_RUN_NAME}        Advanced Test Run - Bulk Update
@{TEST_CASE_IDS}        12345    12346    12347

*** Test Cases ***
Create Test Cycle And Test Run
    [Documentation]    Create test cycle and test run dynamically
    [Tags]    setup    qtest
    
    Log    Creating test cycle in QTest
    ${cycle_id}=    Create QTest Test Cycle    ${TEST_CYCLE_NAME}    Automated test cycle
    Set Suite Variable    ${CYCLE_ID}    ${cycle_id}
    Log    Test Cycle ID: ${cycle_id}
    
    Log    Creating test run in QTest
    ${run_id}=    Create QTest Test Run
    ...    name=${TEST_RUN_NAME}
    ...    test_case_ids=@{TEST_CASE_IDS}
    ...    test_cycle_id=${cycle_id}
    ...    description=Advanced test run with bulk updates
    
    Set Suite Variable    ${RUN_ID}    ${run_id}
    Log    Test Run ID: ${run_id}
    
    Should Not Be Empty    ${run_id}

Verify Available Statuses
    [Documentation]    Verify QTest execution statuses are available
    [Tags]    verification    qtest
    
    @{statuses}=    Get QTest Execution Statuses
    Log Many    @{statuses}
    
    Should Contain    ${statuses}    PASSED
    Should Contain    ${statuses}    FAILED
    Log    Available statuses verified

Bulk Update Test Results
    [Documentation]    Update multiple test results in bulk
    [Tags]    bulk    qtest
    
    # Prepare test results
    ${result1}=    Create Dictionary
    ...    test_case_id=12345
    ...    status=PASSED
    ...    note=Test passed - Login successful
    ...    execution_time=2500
    
    ${result2}=    Create Dictionary
    ...    test_case_id=12346
    ...    status=FAILED
    ...    note=Test failed - Invalid credentials not handled
    ...    execution_time=3200
    
    ${result3}=    Create Dictionary
    ...    test_case_id=12347
    ...    status=SKIPPED
    ...    note=Test skipped - Environment not ready
    
    @{results}=    Create List    ${result1}    ${result2}    ${result3}
    
    Log    Bulk updating ${result1}[test_case_id], ${result2}[test_case_id], ${result3}[test_case_id]
    ${updated}=    Bulk Report QTest Results    ${RUN_ID}    ${results}
    
    Should Not Be Empty    ${updated}
    Log    Bulk update completed: ${updated}

Test With Timer
    [Documentation]    Test with execution time tracking
    [Tags]    timing    qtest
    
    Start Test Timer    timing_test
    
    Log    Executing timed test
    Sleep    2s
    
    ${duration}=    Get Test Duration Ms    timing_test
    Log    Test duration: ${duration}ms
    
    Should Be True    ${duration} >= 2000
    Should Be True    ${duration} < 3000

*** Keywords ***
Advanced Setup
    [Documentation]    Advanced setup with QTest initialization
    Log    Starting advanced QTest integration tests
    Initialize QTest Manager    ${QTEST_CONFIG}
    Log    QTest Manager initialized

Advanced Teardown
    [Documentation]    Advanced teardown with finalization
    Finalize QTest Run
    Log    Advanced QTest integration tests completed
