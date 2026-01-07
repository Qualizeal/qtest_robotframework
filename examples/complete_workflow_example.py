"""
Example: Complete Workflow
This example demonstrates a complete workflow:
1. Create a test cycle
2. Create a test run
3. Execute tests and update results
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from qtest_manager import QTestManager


def main():
    """Complete workflow example"""
    
    # Initialize QTest Manager
    manager = QTestManager('../config.json')
    
    print("=" * 60)
    print("QTest Automation - Complete Workflow Example")
    print("=" * 60)
    
    # Step 1: Create a test cycle
    print("\n[Step 1] Creating test cycle...")
    test_cycle = manager.create_test_cycle(
        name=f"Automated Test Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description="Test cycle created via automation for regression testing"
    )
    print(f"✓ Test Cycle Created: ID={test_cycle['id']}, Name='{test_cycle['name']}'")
    
    # Step 2: Create a test run within the test cycle
    print("\n[Step 2] Creating test run...")
    test_case_ids = [12345, 12346, 12347, 12348, 12349]  # Replace with actual test case IDs
    
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    test_run = manager.create_test_run(
        name=f"Automated Test Run - {start_date.strftime('%Y-%m-%d %H:%M')}",
        test_case_ids=test_case_ids,
        test_cycle_id=test_cycle['id'],
        description="Automated test execution for smoke testing",
        planned_start_date=start_date.isoformat(),
        planned_end_date=end_date.isoformat()
    )
    print(f"✓ Test Run Created: ID={test_run['id']}, Name='{test_run['name']}'")
    
    # Step 3: Simulate test execution and update results
    print("\n[Step 3] Executing tests and updating results...")
    
    # Simulate test execution results
    test_results = [
        {
            'test_case_id': 12345,
            'status': 'PASSED',
            'note': 'Login functionality verified successfully',
            'execution_time': 3500
        },
        {
            'test_case_id': 12346,
            'status': 'PASSED',
            'note': 'User registration completed without errors',
            'execution_time': 4200
        },
        {
            'test_case_id': 12347,
            'status': 'FAILED',
            'note': 'Dashboard loading failed - timeout after 30 seconds',
            'execution_time': 30000,
            'defects': ['DEF-456']
        },
        {
            'test_case_id': 12348,
            'status': 'PASSED',
            'note': 'Search functionality working as expected',
            'execution_time': 2800
        },
        {
            'test_case_id': 12349,
            'status': 'SKIPPED',
            'note': 'Test skipped - prerequisite test failed'
        }
    ]
    
    results = manager.bulk_update_test_results(test_run['id'], test_results)
    
    # Step 4: Summary
    print("\n[Step 4] Test Execution Summary")
    print("-" * 60)
    
    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]
    
    print(f"Test Cycle ID: {test_cycle['id']}")
    print(f"Test Run ID: {test_run['id']}")
    print(f"Total Test Cases: {len(test_results)}")
    print(f"Results Updated: {len(successful)}")
    print(f"Update Failures: {len(failed)}")
    
    # Count by status
    passed = sum(1 for r in test_results if r['status'] == 'PASSED')
    failed_tests = sum(1 for r in test_results if r['status'] == 'FAILED')
    skipped = sum(1 for r in test_results if r['status'] == 'SKIPPED')
    
    print(f"\nTest Results:")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed_tests}")
    print(f"  ⊘ Skipped: {skipped}")
    
    print("\n" + "=" * 60)
    print("Workflow completed successfully!")
    print("=" * 60)
    
    return {
        'test_cycle': test_cycle,
        'test_run': test_run,
        'results': results
    }


if __name__ == "__main__":
    main()
