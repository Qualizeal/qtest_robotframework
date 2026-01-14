*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
${AZURE_LOGIN_BUTTON}           xpath=//*[@alt="Login with Azure"]
${LOGIN_EMAIL_INPUT}            xpath=//*[@name="loginfmt"]
${LOGIN_NEXT_BUTTON}            id=idSIButton9
${LOGIN_PASSWORD_INPUT}         xpath=//*[@name="passwd"]
${LOGIN_SUBMIT_BUTTON}          xpath=//*[@type="submit"]
${LOGIN_STAY_SIGNED_IN_HEADER}  xpath=//*[contains(text(),"Stay signed in?")]



