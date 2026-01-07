"""
Unit tests for QTest Manager
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from qtest_manager import QTestManager


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration file"""
    config_file = tmp_path / "config.json"
    config_data = {
        "qtest_url": "https://test.qtestnet.com",
        "api_token": "test-token-123",
        "project_id": 12345,
        "log_level": "INFO"
    }
    config_file.write_text(json.dumps(config_data))
    return str(config_file)


@pytest.fixture
def qtest_manager(mock_config):
    """Create QTestManager instance with mock config"""
    with patch('qtest_manager.QTestAPI'):
        manager = QTestManager(mock_config)
        return manager


def test_manager_initialization(mock_config):
    """Test QTest Manager initialization"""
    with patch('qtest_manager.QTestAPI'):
        manager = QTestManager(mock_config)
        assert manager.config['qtest_url'] == "https://test.qtestnet.com"
        assert manager.config['project_id'] == 12345


def test_get_execution_statuses(qtest_manager):
    """Test getting execution statuses"""
    mock_statuses = [
        {'id': 1, 'name': 'Passed'},
        {'id': 2, 'name': 'Failed'},
        {'id': 3, 'name': 'Skipped'}
    ]
    
    qtest_manager.api.get_execution_statuses = Mock(return_value=mock_statuses)
    
    statuses = qtest_manager.get_execution_statuses()
    
    assert 'PASSED' in statuses
    assert 'FAILED' in statuses
    assert 'SKIPPED' in statuses
    assert statuses['PASSED'] == 1


def test_create_test_run(qtest_manager):
    """Test creating a test run"""
    mock_response = {
        'id': 100,
        'name': 'Test Run 1',
        'web_url': 'https://test.qtestnet.com/p/12345/portal/project#tab=testexecution&object=2&id=100'
    }
    
    qtest_manager.api.create_test_run = Mock(return_value=mock_response)
    
    result = qtest_manager.create_test_run(
        name="Test Run 1",
        test_case_ids=[1, 2, 3],
        test_cycle_id=50
    )
    
    assert result['id'] == 100
    assert result['name'] == 'Test Run 1'
    qtest_manager.api.create_test_run.assert_called_once()


def test_update_test_result(qtest_manager):
    """Test updating test result"""
    mock_statuses = [
        {'id': 1, 'name': 'Passed'}
    ]
    qtest_manager.api.get_execution_statuses = Mock(return_value=mock_statuses)
    
    mock_test_log = {
        'id': 200,
        'status': {'id': 1, 'name': 'PASSED'},
        'test_case_version_id': 10
    }
    qtest_manager.api.add_test_log = Mock(return_value=mock_test_log)
    
    result = qtest_manager.update_test_result(
        test_run_id=100,
        test_case_id=10,
        status='PASSED',
        note='Test passed successfully'
    )
    
    assert result['id'] == 200
    assert result['status']['name'] == 'PASSED'
    qtest_manager.api.add_test_log.assert_called_once()


def test_bulk_update_test_results(qtest_manager):
    """Test bulk updating test results"""
    mock_statuses = [
        {'id': 1, 'name': 'Passed'},
        {'id': 2, 'name': 'Failed'}
    ]
    qtest_manager.api.get_execution_statuses = Mock(return_value=mock_statuses)
    
    qtest_manager.api.add_test_log = Mock(side_effect=[
        {'id': 201, 'status': {'id': 1, 'name': 'PASSED'}},
        {'id': 202, 'status': {'id': 2, 'name': 'FAILED'}}
    ])
    
    test_results = [
        {'test_case_id': 10, 'status': 'PASSED', 'note': 'Test 1 passed'},
        {'test_case_id': 11, 'status': 'FAILED', 'note': 'Test 2 failed'}
    ]
    
    results = qtest_manager.bulk_update_test_results(100, test_results)
    
    assert len(results) == 2
    assert results[0]['id'] == 201
    assert results[1]['id'] == 202


def test_invalid_status(qtest_manager):
    """Test updating with invalid status"""
    mock_statuses = [
        {'id': 1, 'name': 'Passed'}
    ]
    qtest_manager.api.get_execution_statuses = Mock(return_value=mock_statuses)
    
    with pytest.raises(ValueError, match="Invalid status"):
        qtest_manager.update_test_result(
            test_run_id=100,
            test_case_id=10,
            status='INVALID_STATUS'
        )


def test_ensure_test_run_for_case_found(qtest_manager):
    """Ensure returns existing test run ID without creating a new one."""
    qtest_manager.api.find_test_run_id_by_test_case = Mock(return_value=999)
    qtest_manager.api.create_test_run_for_case = Mock()

    run_id = qtest_manager.ensure_test_run_for_case(
        parent_id=50,
        parent_type='test-suite',
        test_case_id=10
    )

    assert run_id == 999
    qtest_manager.api.create_test_run_for_case.assert_not_called()


def test_ensure_test_run_for_case_create(qtest_manager):
    """Ensure creates a test run when not found and returns new ID."""
    qtest_manager.api.find_test_run_id_by_test_case = Mock(return_value=None)
    qtest_manager.api.create_test_run_for_case = Mock(return_value={'id': 1001})

    run_id = qtest_manager.ensure_test_run_for_case(
        parent_id=50,
        parent_type='test-suite',
        test_case_id=10,
        create_if_missing=True
    )

    assert run_id == 1001
    qtest_manager.api.create_test_run_for_case.assert_called_once()
