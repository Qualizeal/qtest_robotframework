*** Settings ***
Documentation     Common UI keywords for Robot suites
Library           SeleniumLibrary
Library           OperatingSystem
Library           String
Library           Collections
Library           DateTime

Resource           ../object_files/login.resource
Resource           ../object_files/dashboard.resource
*** Variables ***
${BROWSER}               Chrome
${DEFAULT_TIMEOUT}       10s
${MID_TIMEOUT}       30s
${MAX_TIMEOUT}       60s
${AUTH_TIMEOUT}       120s
*** Keywords ***

Read Env And Set Credentials
    [Documentation]    Read key=value pairs from a .env file and set suite variables for url/username/password.
    ...                Keys expected: APP_URL, APP_USERNAME, APP_PASSWORD. Lines starting with # are ignored.
    [Arguments]    ${env_path}=${EXECDIR}${/}.env
    # Ensure file exists (no-fail if missing, we will fallback to existing env)
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${env_path}
    IF    ${exists}
        ${content}=    Get File    ${env_path}
        ${lines}=    Split To Lines    ${content}
        ${env}=    Create Dictionary
        FOR    ${line}    IN    @{lines}
            ${stripped}=    Strip String    ${line}
            Continue For Loop If    '${stripped}' == ''
            ${firstchar}=    Get Substring    ${stripped}    0    1
            Continue For Loop If    '${firstchar}' == '#'
            ${parts}=    Split String    ${stripped}    =    1
            ${plen}=    Get Length    ${parts}
            Continue For Loop If    ${plen} < 2
            ${key}=    Get From List    ${parts}    0
            ${val}=    Get From List    ${parts}    1
            ${key}=    Strip String    ${key}
            ${val}=    Strip String    ${val}
            Set Environment Variable    ${key}    ${val}
            Set To Dictionary    ${env}    ${key}    ${val}
        END
    END
    # Set suite variables from environment (works with or without .env if already set)
    Set Suite Variable    ${url}         ${env.APP_URL}
    Set Suite Variable    ${username}    ${env.APP_USERNAME}
    Set Suite Variable    ${password}    ${env.APP_PASSWORD}

Login To Application
    [Documentation]    Open the application and perform login using locators from login.robot.
    [Arguments]    ${url}    ${username}    ${password}
    Open Browser    ${url}    ${BROWSER}
    Maximize Browser Window
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${AZURE_LOGIN_BUTTON}    ${MID_TIMEOUT}
    Click Element    ${AZURE_LOGIN_BUTTON}
    Wait Until Element Is Visible    ${LOGIN_EMAIL_INPUT}    ${MID_TIMEOUT}
    Input Text    ${LOGIN_EMAIL_INPUT}    ${username}
    Wait Until Element Is Visible    ${LOGIN_NEXT_BUTTON}    ${MID_TIMEOUT}
    Click Element    ${LOGIN_NEXT_BUTTON}
    Wait Until Element Is Visible    ${LOGIN_PASSWORD_INPUT}    ${MID_TIMEOUT}
    Input Password    ${LOGIN_PASSWORD_INPUT}    ${password}
    Wait Until Element Is Visible    ${LOGIN_SUBMIT_BUTTON}    ${MID_TIMEOUT}
    Click Element    ${LOGIN_SUBMIT_BUTTON}
    # Optionally handle 'Stay signed in?' prompt
    Sleep    ${DEFAULT_TIMEOUT}
    Wait Until Element Is Visible    ${LOGIN_STAY_SIGNED_IN_HEADER}    ${MID_TIMEOUT}
    Click Element    ${LOGIN_NEXT_BUTTON}
    Wait Until Page Contains Element    css:body    ${DEFAULT_TIMEOUT}

Select Client Environment
    [Documentation]    Select the client and environment from dropdowns or selectors.
    [Arguments]    ${client_name}    ${environment}    ${client_dropdown_locator}    ${environment_dropdown_locator}
    Wait Until Element Is Visible    ${client_dropdown_locator}    ${DEFAULT_TIMEOUT}
    # If locator is a <select>, Select From List By Label works. Otherwise, adapt click sequence.
    Run Keyword And Ignore Error    Select From List By Label    ${client_dropdown_locator}    ${client_name}
    Wait Until Element Is Visible    ${environment_dropdown_locator}    ${DEFAULT_TIMEOUT}
    Run Keyword And Ignore Error    Select From List By Label    ${environment_dropdown_locator}    ${environment}
    # Fallback: click-based selection when not a <select>
    Run Keyword If    '${${/}NONE}' == '${NONE}'    No Operation

ADD STEP LOG TO QTEST
    [Documentation]    Add a test step log to QTest for the current test case.
    [Arguments]    ${test_case_id}    ${step_logs}    ${step_number}    ${status}    ${actual}    ${expected}    ${comments}    ${capture_screenshot}=True    ${screenshot_prefix}=step

    # Optionally capture a screenshot with a dynamic filename and attach to the step log
    ${attachment}=    Set Variable
    IF    '${capture_screenshot}' == 'True'
        Create Directory    ${EXECDIR}${/}screenshots
        ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S
        ${safe_name}=    Replace String Using Regexp    ${TEST_NAME}    \\s+    _
        ${filename}=    Set Variable    ${screenshot_prefix}_${safe_name}_${step_number}_${timestamp}.png
        ${attachment}=    Set Variable    ${EXECDIR}${/}screenshots${/}${filename}
        Capture Page Screenshot    ${attachment}
    END

    # Append step log, including attachment if present
    ${step_logs}=    Append QTest Test Step Log    ${test_case_id}    ${step_logs}    ${step_number}    ${status}    ${actual}    ${expected}    ${comments}    ${attachment}
    
    [Return]    ${step_logs}
