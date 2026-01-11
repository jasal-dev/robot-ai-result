*** Settings ***
Library    Browser

*** Test Cases **
SAUCE 01 - LOGIN
    [Documentation]  Login with correct credentials and verify that inventory list is visible
    New Browser    chromium    headless=true
    New Context    tracing=${TRUE}    viewport={'width': 1920, 'height': 1080}
    New Page    https://www.saucedemo.com/
    Type Text   [data-test="username"]    admin_user
    Type Text   [data-test="password"]    secret_sauce
    Click       [data-test="login-button"]
    Wait For Elements State    [data-test="inventory-list"]    visible
    [Teardown]  Close Browser    ALL
