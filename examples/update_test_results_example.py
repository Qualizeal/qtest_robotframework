"""
Example: Update Test Results
This example demonstrates how to update test case results in QTest
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from qtest_manager import QTestManager


def main():
    """Update test results for multiple test cases"""
    
    # Initialize QTest Manager
    manager = QTestManager('../config.json')
    
    # Test run ID where results will be updated
    test_run_id = 123456
    
    # Example 1: Update single test result
    print("Updating single test result...")
    result = manager.update_test_result(
        test_run_id=test_run_id,
        test_case_id=12345,
        status="PASSED",
        note="Test executed successfully. All assertions passed.",
        execution_time=5000  # 5 seconds in milliseconds
    )
    print(f"Test Log ID: {result['id']}")
    print(f"Status: {result['status']['name']}")
    
    # Example 2: Update test result with failure
    print("\nUpdating failed test result...")
    result = manager.update_test_result(
        test_run_id=test_run_id,
        test_case_id=12346,
        status="FAILED",
        note="Test failed: Expected value 'Hello' but got 'World'",
        execution_time=3000,
        defects=["DEF-123"]  # Link to defect ID
    )
    print(f"Test Log ID: {result['id']}")
    print(f"Status: {result['status']['name']}")
    
    # Example 3: Bulk update test results
    print("\nBulk updating test results...")
    test_results = [
        {
            'test_case_id': 12347,
            'status': 'PASSED',
            'note': 'Login test passed',
            'execution_time': 2000
        },
        {
            'test_case_id': 12348,
            'status': 'SKIPPED',
            'note': 'Test skipped due to environment issue'
        },
        {
            'test_case_id': 12349,
            'status': 'PASSED',
            'note': 'Data validation test passed',
            'execution_time': 4500
        }
    ]
    
    results = manager.bulk_update_test_results(test_run_id, test_results)
    
    print(f"\nBulk update completed!")
    print(f"Total results updated: {len(results)}")
    print(f"Successful: {len([r for r in results if 'error' not in r])}")
    print(f"Failed: {len([r for r in results if 'error' in r])}")
    
    # Example 4: Get available statuses
    print("\nAvailable execution statuses:")
    statuses = manager.get_available_statuses()
    for status in statuses:
        print(f"  - {status}")
    
    return results


if __name__ == "__main__":
    main()
