*** Settings ***
Documentation     Dashboard page object: locators and common names

*** Variables ***
# Page headers and common widgets
# ${LABEL_ALIASES_LINK}           xpath=(//a[contains(@href,"general/aliases")])[2]
${LABEL_ALIASES_LINK}                    xpath=(//a[@href='/settings/general/aliases'])[2]
${LABEL_READ_ONLY_FIELDS_LINK}           xpath=(//a[@href='/settings/general/readOnlyFields'])[2]
${LABEL_ALIASES_SEARCH_INPUT}            xpath=//*[@id="search"]
${LABEL_ALIASES_SEARCH_INPUT_RESULT}            xpath=//h1[text()="Label Aliases"]/following::table/tbody/tr[1]/td[position() > 1]
${LABEL_READ_ONLY_FIELDS_SEARCH_INPUT_RESULT}            xpath=//h1[text()="Read-only Fields"]/following::table/tbody/tr[1]/td[position() > 1]
${PAGECONTAINS404}                        xpath=//*[text()="404 Not Found"]
