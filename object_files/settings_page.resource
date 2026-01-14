*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
# ${LABEL_ALIASES_LINK}           xpath=(//a[contains(@href,"general/aliases")])[2]
${LABEL_ALIASES_LINK}           xpath=(//a[@href='/settings/general/aliases'])[2]
${LABEL_ALIASES_SEARCH_INPUT}        xpath=//*[@id="search"]
