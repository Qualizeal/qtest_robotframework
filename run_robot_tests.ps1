# Run Robot Framework QTest Integration Tests
# PowerShell script to run tests

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Robot Framework QTest Tests" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Robot Framework is installed
try {
    python -c "import robot" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Robot Framework not installed"
    }
    Write-Host "✓ Robot Framework is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Robot Framework is not installed!" -ForegroundColor Red
    Write-Host "Please run: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create results directory if it doesn't exist
if (!(Test-Path "test_results")) {
    New-Item -ItemType Directory -Path "test_results" | Out-Null
}

Write-Host "Select test suite to run:" -ForegroundColor Yellow
Write-Host "1. Simple QTest Test (basic example)"
Write-Host "2. QTest Integration Tests (comprehensive)"
Write-Host "3. Advanced QTest Tests (bulk updates)"
Write-Host "4. All Tests"
Write-Host "5. All Tests with Specific Tag"
Write-Host "6. Run with Report Only (no logs)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running Simple QTest Test..." -ForegroundColor Cyan
        robot --outputdir test_results tests\robot\simple_qtest_test.robot
    }
    "2" {
        Write-Host ""
        Write-Host "Running QTest Integration Tests..." -ForegroundColor Cyan
        robot --outputdir test_results tests\robot\qtest_integration_tests.robot
    }
    "3" {
        Write-Host ""
        Write-Host "Running Advanced QTest Tests..." -ForegroundColor Cyan
        robot --outputdir test_results tests\robot\advanced_qtest_tests.robot
    }
    "4" {
        Write-Host ""
        Write-Host "Running All Tests..." -ForegroundColor Cyan
        robot --outputdir test_results tests\robot\
    }
    "5" {
        Write-Host ""
        $tag = Read-Host "Enter tag to run (smoke, qtest, functional, critical)"
        Write-Host "Running Tests with tag: $tag" -ForegroundColor Cyan
        robot --outputdir test_results --include $tag tests\robot\
    }
    "6" {
        Write-Host ""
        Write-Host "Running with minimal output..." -ForegroundColor Cyan
        robot --outputdir test_results --loglevel WARN tests\robot\
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Test execution completed!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Results saved in: test_results\" -ForegroundColor Yellow
Write-Host "View report.html for detailed results" -ForegroundColor Yellow
Write-Host ""

# Open report if exists
if (Test-Path "test_results\report.html") {
    $openReport = Read-Host "Open report in browser? (y/n)"
    if ($openReport -eq "y" -or $openReport -eq "Y") {
        Start-Process "test_results\report.html"
    }
}

Write-Host ""
Read-Host "Press Enter to exit"
