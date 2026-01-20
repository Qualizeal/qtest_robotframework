*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
${LASTACTIVITY_HEADER}      xpath=//*[contains(text(),"Last Activity")]
${PROFILEBUTTON}           xpath=//button[@id="user-menu"]
${SETTINGS_LINK}           xpath=//a[contains(text(),"Settings")]