"""
Robot Framework QTest Integration - Quick Test
Validates that Robot Framework can successfully integrate with QTest
"""

from pathlib import Path
import subprocess
import sys


def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    dependencies = {
        'robot': 'Robot Framework',
        'requests': 'Requests library',
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name} is installed")
        except ImportError:
            print(f"✗ {name} is NOT installed")
            missing.append(name)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies are installed!")
    return True


def check_config():
    """Check if configuration file exists"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("\n✗ config.json not found!")
        print("Please create config.json with your QTest credentials")
        print("Run: python quick_start.py")
        return False
    
    print("✓ Configuration file exists")
    return True


def run_simple_test():
    """Run a simple Robot Framework test"""
    print("\n" + "="*60)
    print("Running Simple Robot Framework QTest Test")
    print("="*60 + "\n")
    
    test_file = Path("tests/robot/simple_qtest_test.robot")
    
    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False
    
    try:
        # Run robot test
        result = subprocess.run(
            [
                sys.executable, "-m", "robot",
                "--outputdir", "test_results",
                "--loglevel", "INFO",
                str(test_file)
            ],
            capture_output=False
        )
        
        if result.returncode == 0:
            print("\n✓ Robot Framework test executed successfully!")
            print("\nResults saved in: test_results/")
            print("View report.html for detailed results")
            return True
        else:
            print(f"\n✗ Test execution failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error running test: {str(e)}")
        return False


def main():
    """Main validation function"""
    print("="*60)
    print("Robot Framework QTest Integration - Validation")
    print("="*60 + "\n")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Step 2: Check configuration
    if not check_config():
        sys.exit(1)
    
    print()
    
    # Step 3: Ask user if they want to run test
    response = input("Run a simple test now? (y/n): ").lower()
    
    if response == 'y':
        success = run_simple_test()
        sys.exit(0 if success else 1)
    else:
        print("\nValidation completed. You can run tests manually using:")
        print("  robot tests/robot/simple_qtest_test.robot")
        print("  or")
        print("  python run_robot_tests.ps1")


if __name__ == "__main__":
    main()
