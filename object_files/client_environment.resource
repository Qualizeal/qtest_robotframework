*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
${CLIENT_ENVIRONMENT_PAGE_TITLE}           xpath=//*[text()='Client Environments']
${CLIENT_ENVIRONMENT_ACTION_BUTTON}         xpath=//*[contains(text(),"Test")]/following-sibling::td//*[@class='table-action mr-3']
${CLIENT_ENVIRONMENT_CONFIRM_BUTTON}        xpath=//*[@class="button button-confirm"]

${CLIENT_ENVIRONMENT_AUTH_LINK}        xpath=//a//*[contains(text(),'Auth')]
${CLIENT_ENVIRONMENT_LOGIN_REASON_INPUT}        xpath=//*[@placeholder="I need to login because ..."]
${CLIENT_ENVIRONMENT_ADMINISTRATOR_BUTTON}        xpath=//p[normalize-space()='Administrator']/ancestor::button
