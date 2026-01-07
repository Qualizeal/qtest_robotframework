"""
Quick Start Guide
Run this script to set up and test your QTest integration
"""

import json
import sys
from pathlib import Path


def main():
    """Quick start setup wizard"""
    
    print("=" * 70)
    print("QTest Automation - Quick Start Setup")
    print("=" * 70)
    print()
    
    # Check if config exists
    config_path = Path("config.json")
    
    if config_path.exists():
        print("⚠ config.json already exists!")
        response = input("Do you want to reconfigure? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled. Using existing configuration.")
            return
    
    print("\nPlease provide your QTest details:")
    print("-" * 70)
    
    # Get user input
    qtest_url = input("QTest URL (e.g., https://your-domain.qtestnet.com): ").strip()
    api_token = input("API Token: ").strip()
    project_id = input("Project ID: ").strip()
    
    # Validate inputs
    if not qtest_url or not api_token or not project_id:
        print("\n✗ Error: All fields are required!")
        sys.exit(1)
    
    try:
        project_id = int(project_id)
    except ValueError:
        print("\n✗ Error: Project ID must be a number!")
        sys.exit(1)
    
    # Create configuration
    config = {
        "qtest_url": qtest_url,
        "api_token": api_token,
        "project_id": project_id,
        "default_test_cycle_id": None,
        "log_level": "INFO"
    }
    
    # Save configuration
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✓ Configuration saved successfully!")
    print("=" * 70)
    
    print("\nNext Steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run example scripts in the 'examples' folder:")
    print("   - python examples/create_test_run_example.py")
    print("   - python examples/update_test_results_example.py")
    print("   - python examples/complete_workflow_example.py")
    print()
    print("For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
