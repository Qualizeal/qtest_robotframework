@echo off
REM Run Robot Framework QTest Integration Tests
REM This batch file runs all Robot Framework test suites

echo ====================================
echo Robot Framework QTest Tests
echo ====================================
echo.

REM Check if Robot Framework is installed
python -c "import robot" 2>nul
if errorlevel 1 (
    echo ERROR: Robot Framework is not installed!
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo Robot Framework is installed
echo.

REM Create results directory if it doesn't exist
if not exist "test_results" mkdir test_results

echo Select test suite to run:
echo 1. Simple QTest Test (basic example)
echo 2. QTest Integration Tests (comprehensive)
echo 3. Advanced QTest Tests (bulk updates)
echo 4. All Tests
echo 5. All Tests with Tags
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running Simple QTest Test...
    robot --outputdir test_results tests\robot\simple_qtest_test.robot
) else if "%choice%"=="2" (
    echo.
    echo Running QTest Integration Tests...
    robot --outputdir test_results tests\robot\qtest_integration_tests.robot
) else if "%choice%"=="3" (
    echo.
    echo Running Advanced QTest Tests...
    robot --outputdir test_results tests\robot\advanced_qtest_tests.robot
) else if "%choice%"=="4" (
    echo.
    echo Running All Tests...
    robot --outputdir test_results tests\robot\
) else if "%choice%"=="5" (
    echo.
    set /p tag="Enter tag to run (smoke, qtest, functional): "
    echo Running Tests with tag: %tag%
    robot --outputdir test_results --include %tag% tests\robot\
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo ====================================
echo Test execution completed!
echo ====================================
echo.
echo Results saved in: test_results\
echo View report.html for detailed results
echo.
pause
