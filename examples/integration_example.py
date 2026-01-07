"""
QTest Integration Example for Test Automation Framework
This shows how to integrate QTest updates into your existing test framework
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from qtest_manager import QTestManager


class QTestReporter:
    """Reporter class for integrating QTest with test frameworks"""
    
    def __init__(self, config_path: str = '../config.json'):
        """Initialize QTest reporter"""
        self.manager = QTestManager(config_path)
        self.test_run_id = None
        self.test_results = []
    
    def start_test_run(self, name: str, test_case_ids: list, test_cycle_id: int = None):
        """Start a new test run"""
        test_run = self.manager.create_test_run(
            name=name,
            test_case_ids=test_case_ids,
            test_cycle_id=test_cycle_id
        )
        self.test_run_id = test_run['id']
        print(f"Started Test Run: {name} (ID: {self.test_run_id})")
        return self.test_run_id
    
    def report_test_result(self, test_case_id: int, status: str, 
                          message: str = "", execution_time: int = 0):
        """Report individual test result"""
        if not self.test_run_id:
            raise ValueError("Test run not started. Call start_test_run() first.")
        
        self.test_results.append({
            'test_case_id': test_case_id,
            'status': status,
            'note': message,
            'execution_time': execution_time
        })
    
    def finalize_test_run(self):
        """Finalize and upload all test results"""
        if not self.test_run_id:
            raise ValueError("Test run not started.")
        
        results = self.manager.bulk_update_test_results(
            self.test_run_id, 
            self.test_results
        )
        
        print(f"\nTest Run Completed: ID {self.test_run_id}")
        print(f"Total Results: {len(results)}")
        print(f"Successfully Updated: {len([r for r in results if 'error' not in r])}")
        
        return results


# Example usage with pytest-like structure
def example_test_suite():
    """Example showing how to use QTestReporter in a test suite"""
    
    # Initialize reporter
    reporter = QTestReporter()
    
    # Start test run
    test_case_ids = [12345, 12346, 12347]
    reporter.start_test_run(
        name="Automated Test Suite - Login Flow",
        test_case_ids=test_case_ids,
        test_cycle_id=100
    )
    
    # Simulate test execution
    try:
        # Test 1
        print("Running Test Case 12345...")
        # Your test logic here
        reporter.report_test_result(
            test_case_id=12345,
            status='PASSED',
            message='Login with valid credentials successful',
            execution_time=3500
        )
        
        # Test 2
        print("Running Test Case 12346...")
        # Your test logic here
        reporter.report_test_result(
            test_case_id=12346,
            status='PASSED',
            message='Login with invalid credentials properly rejected',
            execution_time=2800
        )
        
        # Test 3
        print("Running Test Case 12347...")
        # Your test logic here
        reporter.report_test_result(
            test_case_id=12347,
            status='FAILED',
            message='Password reset link not working',
            execution_time=5000
        )
        
    finally:
        # Always finalize, even if tests fail
        reporter.finalize_test_run()


if __name__ == "__main__":
    example_test_suite()
