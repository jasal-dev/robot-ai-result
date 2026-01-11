*** Settings ***
Library    Browser

*** Test Cases **
SAUCE 01 - LOGIN
    [Documentation]  Login with correct credentials and verify that inventory list is visible
    New Page    https://www.saucedemo.com/
    Type Text   [data-test="username"]    locked_out_user
    Type Text   [data-test="password"]    secret_sauce
    Click       [data-test="login-button"]
    Wait For Elements State    [data-test="inventory-list"]    visible
