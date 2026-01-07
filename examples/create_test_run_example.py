"""
Example: Create Test Run
This example demonstrates how to create a test run in QTest
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from qtest_manager import QTestManager


def main():
    """Create a test run with multiple test cases"""
    
    # Initialize QTest Manager
    manager = QTestManager('../config.json')
    
    # Test case IDs to include in the test run
    test_case_ids = [12345, 12346, 12347]
    
    # Create test run
    test_run = manager.create_test_run(
        name="Automated Test Run - Example",
        test_case_ids=test_case_ids,
        test_cycle_id=100,  # Optional: specify a test cycle
        description="This is an example test run created via API",
        planned_start_date="2026-01-06T10:00:00Z",
        planned_end_date="2026-01-06T18:00:00Z"
    )
    
    print(f"Test Run Created Successfully!")
    print(f"Test Run ID: {test_run['id']}")
    print(f"Test Run Name: {test_run['name']}")
    print(f"Test Run URL: {test_run.get('web_url', 'N/A')}")
    
    return test_run


if __name__ == "__main__":
    main()
