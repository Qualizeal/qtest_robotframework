*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
${WELCOME_BACK_HEADER}           xpath=//*[contains(text(),"Welcome back")]
${WELCOME_BACK_SEARCH_INPUT}     id=search
${DASHBOARD_PAGE_TITLE}           xpath=//h1[normalize-space()='Dashboard']
${CLIENT_NAME}    xpath=//*[text()='{}']/..


