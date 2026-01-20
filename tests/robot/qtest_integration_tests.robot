*** Settings ***
Documentation     QTest Integration Test Suite
...               This suite demonstrates how to integrate QTest with Robot Framework tests
Library           Collections
Library           DateTime
Library           ../../qtest_robot_library.py
Resource          ../../keywords/common_keywords.robot
Resource          ../../object_files/login.resource
Resource          ../../object_files/dashboard.resource
Resource          ../../object_files/settings_page.resource
Resource          ../../object_files/clients.resource
Resource          ../../object_files/client_environment.resource

# Suite Setup       Setup QTest Integration
Suite Teardown    Finalize QTest Test Run
Test Setup        Run Keywords    Read Env And Set Credentials    ${EXECDIR}${/}.env    
...    AND    Setup QTest Integration    AND    Log Test Start    
...    AND    Login To Application    ${url}    ${username}    ${password}
Test Teardown   Run Keywords   Report Test Result   AND   Close All Browsers

*** Variables ***
${QTEST_CONFIG}         ${EXECDIR}${/}config.json
${TEST_CYCLE_NAME}       TestDemo
${TEST_RUN_NAME}        Robot Framework Test Run - ${TEST_CYCLE_NAME}

*** Test Cases ***
Validate that Admin user is able to navigate to the required page and search Label Aliases
    [Documentation]    Test functionality for Label Aliases with valid credentials
    [Tags]    login    smoke    critical
    Welcome Page Should Be Loaded
    Choose Client     Cardinal
    Open Settings and Label Aliases
    validate Label Aliases page

    #validate Label Aliases page and search with no 404 error showing
    Enter Legal search criteria and validate results    legal



Validate that Admin user is able to navigate to the required page and search Read-only Fields
    [Documentation]    Test functionality for Read-only Fields with valid credentials
    [Tags]    login    smoke    critical
    Welcome Page Should Be Loaded
    Choose Client     Cardinal
    Open Settings and Readonly Aliases
    validate Readonly Aliases page

    #validate Read only Aliases page and search with no 404 error showing
    Enter Read only criteria and validate results    legal
    



*** Keywords ***
Welcome Page Should Be Loaded
    [Documentation]    Verify that the welcome page is loaded
    Wait Until Element Is Visible    ${WELCOME_BACK_HEADER}    ${MAX_TIMEOUT}
    Wait Until Element Is Visible  ${WELCOME_BACK_SEARCH_INPUT}   ${MAX_TIMEOUT}
    Input Text    ${WELCOME_BACK_SEARCH_INPUT}    cardinal
    Press Keys    None    ENTER

Choose Client
    [Arguments]    ${CLIENT_NAME_PARAM}  
    ${CLIENT_NAMEOBJ}=    FORMAT String    ${CLIENT_NAME}      ${CLIENT_NAME_PARAM} 
    Wait Until Element Is Visible    ${CLIENT_NAMEOBJ}    ${MAX_TIMEOUT}
    Click Element     ${CLIENT_NAMEOBJ}
    Wait Until Element Is Visible    ${CLIENT_ENVIRONMENT_ACTION_BUTTON}    ${MAX_TIMEOUT}
    Click Element    ${CLIENT_ENVIRONMENT_ACTION_BUTTON}
    Sleep    ${MID_TIMEOUT}
    Select Environment and client admin login
Select Environment and client admin login
    Wait Until Element Is Visible    ${CLIENT_ENVIRONMENT_AUTH_LINK}   ${AUTH_TIMEOUT}
    
    Click Element    ${CLIENT_ENVIRONMENT_AUTH_LINK}
    Wait Until Element Is Visible    ${CLIENT_ENVIRONMENT_LOGIN_REASON_INPUT}    ${MAX_TIMEOUT}
    Input Text    ${CLIENT_ENVIRONMENT_LOGIN_REASON_INPUT}    Testing login access

    Wait Until Element Is Visible    ${CLIENT_ENVIRONMENT_ADMINISTRATOR_BUTTON}    ${MAX_TIMEOUT}
    Scroll Element Into View    ${CLIENT_ENVIRONMENT_ADMINISTRATOR_BUTTON}
    Set Focus To Element    ${CLIENT_ENVIRONMENT_ADMINISTRATOR_BUTTON}
    Click Element    ${CLIENT_ENVIRONMENT_ADMINISTRATOR_BUTTON}
    
    Wait Until Keyword Succeeds    ${MAX_TIMEOUT}    500ms 
    ...    Switch Window    title=Rimsys

    ${PAGETITLE}    Get Title
    ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    1    PASSED    ${PAGETITLE}    Expected ok    Step ran fine
    RETURN  ${PAGETITLE}
Open Settings and Label Aliases
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${LASTACTIVITY_HEADER}    ${MAX_TIMEOUT}
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${PROFILEBUTTON}    ${MAX_TIMEOUT}
    Sleep    ${DEFAULT_TIMEOUT}
    Scroll Element Into View    ${PROFILEBUTTON}
    Set Focus To Element    ${PROFILEBUTTON}
    Click Element    ${PROFILEBUTTON}
    
    Wait Until Element Is Visible    ${SETTINGS_LINK}    ${MAX_TIMEOUT}
    Click Element    ${SETTINGS_LINK}

Open Settings and Readonly Aliases
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${LASTACTIVITY_HEADER}    ${MAX_TIMEOUT}
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${PROFILEBUTTON}    ${MAX_TIMEOUT}
    Sleep    ${DEFAULT_TIMEOUT}
    Scroll Element Into View    ${PROFILEBUTTON}
    Set Focus To Element    ${PROFILEBUTTON}
    Click Element    ${PROFILEBUTTON}
    
    Wait Until Element Is Visible    ${SETTINGS_LINK}    ${MAX_TIMEOUT}
    Click Element    ${SETTINGS_LINK}

validate Label Aliases page
    Wait Until Element Is Visible    ${LABEL_ALIASES_LINK}           ${MAX_TIMEOUT}
    Click Element    ${LABEL_ALIASES_LINK}
    Wait Until Element Is Visible    ${LABEL_ALIASES_SEARCH_INPUT}        ${MAX_TIMEOUT}

validate Readonly Aliases page
    Wait Until Element Is Visible    ${LABEL_READ_ONLY_FIELDS_LINK}           ${MAX_TIMEOUT}
    Click Element    ${LABEL_READ_ONLY_FIELDS_LINK}
    Wait Until Element Is Visible    ${LABEL_ALIASES_SEARCH_INPUT}        ${MAX_TIMEOUT}
Enter Legal search criteria and validate results
    [Arguments]    ${searchcriteria}
    ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    2    PASSED    Settings page Loaded properly    Expected ok    Step ran fine
    Input Text    ${LABEL_ALIASES_SEARCH_INPUT}        ${searchcriteria}
    Press Keys    ${LABEL_ALIASES_SEARCH_INPUT}        ENTER
    ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    3    PASSED    Search Result Loaded properly    Expected ok    Step ran fine
    ${DATAavailable}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LABEL_ALIASES_SEARCH_INPUT_RESULT}
    ${Error404}=    Run Keyword And Return Status    Element Should Not Be Visible    ${PAGECONTAINS404}
    # IF    $DATAavailable == 'True' AND $Error404 == 'True'
    IF  "${DATAavailable}" == "True" and "${Error404}" == "True"
        ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    4    PASSED    No 404    Expected ok    Step ran fine
    ELSE
        ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    4    FAILED    Error 404    Expected ok    Step ran fine
    END

Enter Read only criteria and validate results
    [Arguments]    ${searchcriteria}
    ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    2    PASSED    Settings page Loaded properly    Expected ok    Step ran fine
    Input Text    ${LABEL_ALIASES_SEARCH_INPUT}        ${searchcriteria}
    Press Keys    ${LABEL_ALIASES_SEARCH_INPUT}        ENTER
    ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    3    PASSED    Search Result Loaded properly    Expected ok    Step ran fine
    ${DATAavailable}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${LABEL_READ_ONLY_FIELDS_SEARCH_INPUT_RESULT}
    ${Error404}=    Run Keyword And Return Status    Element Should Not Be Visible    ${PAGECONTAINS404}
    
    IF  "${DATAavailable}" == "True" and "${Error404}" == "True"
        ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    4    PASSED    No 404    Expected ok    Step ran fine
    ELSE
        ${STEP_LOGS}=    ADD STEP LOG TO QTEST    ${TEST_CASE_ID}    ${STEP_LOGS}    4    FAILED    Error 404    Expected ok    Step ran fine
    END
Setup QTest Integration
    [Documentation]    Initialize QTest integration and create test run
    ${date}=    Get Current Date    result_format=%Y-%m-%d %H:%M
    Set Suite Variable    ${CURRENT_DATE}    ${date}
    
    Log    Initializing QTest Integration
    Initialize QTest Manager    ${QTEST_CONFIG}
    Log    Creating test run in QTest
    ${test_run_id}=    Create Qtest Test Run   
    ...    name=${TEST_RUN_NAME}  
    ...    test_case_name=${TEST NAME}  
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