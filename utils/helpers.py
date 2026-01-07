"""
Helper utility functions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any


def format_date_for_qtest(date_obj: datetime) -> str:
    """
    Format datetime object for QTest API
    
    Args:
        date_obj: datetime object
        
    Returns:
        ISO formatted date string
    """
    return date_obj.isoformat()


def parse_test_results_from_dict(results_dict: Dict) -> List[Dict]:
    """
    Parse test results from a dictionary format
    
    Args:
        results_dict: Dictionary containing test results
        
    Returns:
        List of test result dictionaries
    """
    test_results = []
    
    for test_case_id, result in results_dict.items():
        test_results.append({
            'test_case_id': int(test_case_id),
            'status': result.get('status', 'PASSED'),
            'note': result.get('note', ''),
            'execution_time': result.get('execution_time', 0),
            'defects': result.get('defects', [])
        })
    
    return test_results


def calculate_test_summary(test_results: List[Dict]) -> Dict:
    """
    Calculate summary statistics from test results
    
    Args:
        test_results: List of test result dictionaries
        
    Returns:
        Summary dictionary with statistics
    """
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get('status', '').upper() == 'PASSED')
    failed = sum(1 for r in test_results if r.get('status', '').upper() == 'FAILED')
    skipped = sum(1 for r in test_results if r.get('status', '').upper() == 'SKIPPED')
    
    total_execution_time = sum(r.get('execution_time', 0) for r in test_results)
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'pass_rate': (passed / total * 100) if total > 0 else 0,
        'total_execution_time': total_execution_time,
        'avg_execution_time': (total_execution_time / total) if total > 0 else 0
    }


def format_execution_time(milliseconds: int) -> str:
    """
    Format execution time from milliseconds to readable string
    
    Args:
        milliseconds: Execution time in milliseconds
        
    Returns:
        Formatted time string (e.g., "1m 30s")
    """
    seconds = milliseconds / 1000
    
    if seconds < 60:
        return f"{seconds:.2f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m"
