"""
QTest API Wrapper
Handles all HTTP requests to QTest API
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime


class QTestAPI:
    """QTest API wrapper for making HTTP requests"""
    
    def __init__(self, base_url: str, api_token: str, project_id: int):
        """
        Initialize QTest API client
        
        Args:
            base_url: QTest base URL (e.g., https://your-domain.qtestnet.com)
            api_token: QTest API token
            project_id: QTest project ID
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.project_id = project_id
        # Normalize Authorization header to use Bearer schema (as per qTest examples)
        token = api_token or ""
        if token and not token.lower().startswith("bearer "):
            token = f"Bearer {token}"
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
        

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request to QTest API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data as dictionary or None
        """
        url = f"{self.base_url}/api/v3/projects/{self.project_id}/{endpoint}"
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return None
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"Response: {e.response.text}")
            raise
    
    def get_test_case(self, test_case_id: int) -> Dict:
        """Get test case details"""
        return self._make_request('GET', f'test-cases/{test_case_id}')
    
    def get_test_run(self, test_run_id: int) -> Dict:
        """Get test run details"""
        return self._make_request('GET', f'test-runs/{test_run_id}')
    
    def create_test_run(self, test_run_data: Dict, parent_id: Optional[int] = None, parent_type: Optional[str] = None) -> Dict:
        """
        Create a new test run
        
        Args:
            test_run_data: Test run data dictionary
            
        Returns:
            Created test run details
        """
        params = None
        if parent_id and parent_type:
            params = { 'parentId': parent_id, 'parentType': parent_type }
        return self._make_request('POST', 'test-runs', data=test_run_data, params=params)
    
    def update_test_run(self, test_run_id: int, test_run_data: Dict) -> Dict:
        """Update existing test run"""
        return self._make_request('PUT', f'test-runs/{test_run_id}', data=test_run_data)
    
    def add_test_log(self, test_run_id: int, test_log_data: Dict) -> Dict:
        """
        Add test log (execution result) to a test run
        
        Args:
            test_run_id: Test run ID
            test_log_data: Test log data including status, note, etc.
            
        Returns:
            Created test log details
        """
        return self._make_request('POST', f'test-runs/{test_run_id}/test-logs', data=test_log_data)
    
    def update_test_log(self, test_log_id: int, test_log_data: Dict) -> Dict:
        """Update existing test log"""
        return self._make_request('PUT', f'test-logs/{test_log_id}', data=test_log_data)

    def approve_test_case(self, test_case_id: int) -> Dict:
        """
        Approve a test case version in qTest.

        Endpoint: PUT /api/v3/projects/{projectId}/test-cases/{testCaseId}/approve
        """
        return self._make_request('PUT', f'test-cases/{test_case_id}/approve')
    
    def get_test_logs(self, test_run_id: int) -> List[Dict]:
        """Get all test logs for a test run"""
        return self._make_request('GET', f'test-runs/{test_run_id}/test-logs')

    def get_test_steps(self, test_case_id: int) -> List[Dict]:
        """
        Get all test steps for a given test case.
        Endpoint (typical): GET /api/v3/projects/{projectId}/test-cases/{testCaseId}/test-steps
        Returns a list or an object with 'items'; normalize to a list.
        """
        data = self._make_request('GET', f'test-cases/{test_case_id}/test-steps')
        if isinstance(data, dict) and 'items' in data:
            return data.get('items', [])
        if isinstance(data, list):
            return data
        return []

    def find_test_step_id_by_order(self, test_case_id: int, step_number: int) -> Optional[int]:
        """
        Find a test step ID by its order/index within the test case.
        Tries common keys: order, index, sequence, position.
        """
        steps = self.get_test_steps(test_case_id) or []
        for s in steps:
            order = s.get('order') or s.get('index') or s.get('sequence') or s.get('position')
            if order is None:
                continue
            try:
                if int(order) == int(step_number):
                    return s.get('id')
            except Exception:
                # fallback to string equality
                if str(order).strip() == str(step_number).strip():
                    return s.get('id')
        return None
    
    def get_field_settings(self) -> List[Dict]:
        """Get project field settings"""
        return self._make_request('GET', 'settings/test-runs/fields')
    
    def get_execution_statuses(self) -> List[Dict]:
        """Get available execution statuses"""
        return self._make_request('GET', 'test-runs/execution-statuses')
    
    def get_test_cycles(self) -> List[Dict]:
        """Get all test cycles in the project"""
        return self._make_request('GET', 'test-cycles')
    
    def create_test_cycle(self, test_cycle_data: Dict, parent_id: Optional[int] = None, parent_type: Optional[str] = None) -> Dict:
        """Create a new test cycle; optionally under a parent via query params."""
        params = None
        if parent_id and parent_type:
            params = { 'parentId': parent_id, 'parentType': parent_type }
        return self._make_request('POST', 'test-cycles', data=test_cycle_data, params=params)

    # ------- Additional helpers aligned with reference implementation -------
    def get_test_cycles_under(self, parent_cycle_id: int) -> List[Dict]:
        """Get test cycles under a parent cycle."""
        return self._make_request('GET', 'test-cycles', params={ 'parentId': parent_cycle_id, 'parentType': 'test-cycle' })

    def get_test_suites_under_cycle(self, parent_cycle_id: int) -> List[Dict]:
        """Get test suites under a given test cycle."""
        return self._make_request('GET', 'test-suites', params={ 'parentId': parent_cycle_id, 'parentType': 'test-cycle' })

    def create_test_suite_under_cycle(self, parent_cycle_id: int, suite_data: Dict) -> Dict:
        """Create a new test suite under a given test cycle."""
        return self._make_request('POST', 'test-suites', data=suite_data, params={ 'parentId': parent_cycle_id, 'parentType': 'test-cycle' })

    def get_test_runs(self, parent_id: int, parent_type: str, page_size: int = 1000) -> List[Dict]:
        """Get test runs under a given parent (test-suite, test-cycle, release)."""
        data = self._make_request('GET', 'test-runs', params={
            'parentId': parent_id,
            'parentType': parent_type,
            'pageSize': page_size
        })
        if isinstance(data, dict) and 'items' in data:
            return data.get('items', [])
        if isinstance(data, list):
            return data
        return []

    def find_test_run_id_by_test_case(self, parent_id: int, parent_type: str, test_case_id: int) -> Optional[int]:
        """Find an existing test run ID for a given test case under the specified parent."""
        runs = self.get_test_runs(parent_id, parent_type) or []
        for r in runs:
            tc = r.get('test_case') or {}
            if str(tc.get('id')) == str(test_case_id):
                return r.get('id')
        return None

    def create_test_run_for_case(self, parent_id: int, parent_type: str, test_case_id: int,
                                 name: Optional[str] = None,
                                 exe_start_date: Optional[str] = None,
                                 exe_end_date: Optional[str] = None) -> Dict:
        """
        Create a single test run for a specific test case under a parent container (e.g., test-suite).
        Name defaults to the test case name if not provided.
        """
        tc = self.get_test_case(test_case_id)
        payload: Dict[str, Any] = {
            'name': name or tc.get('name', f'Test Run for {test_case_id}'),
            'test_case': {'id': test_case_id}
        }
        if exe_start_date:
            payload['exe_start_date'] = exe_start_date
        if exe_end_date:
            payload['exe_end_date'] = exe_end_date
        return self._make_request('POST', 'test-runs', data=payload, params={ 'parentId': parent_id, 'parentType': parent_type })

    # -------- Name-based lookup helpers --------
    def list_test_cases(self, page_size: int = 100) -> List[Dict]:
        """
        List all test cases in the project with simple pagination.
        Note: Depending on project size, consider narrowing via name matching after fetching pages.
        """
        all_cases: List[Dict] = []
        page = 1
        while True:
            resp = self._make_request('GET', 'test-cases', params={'page': page, 'size': page_size})
            if not resp:
                break
            if isinstance(resp, list):
                if len(resp) == 0:
                    break
                all_cases.extend(resp)
            else:
                # Some deployments may return an object with 'items'
                items = resp.get('items') if isinstance(resp, dict) else None
                if not items:
                    break
                all_cases.extend(items)
                # If a total/pages is present, we could iterate accordingly; here we fall back to length check.
                if len(items) == 0:
                    break
            page += 1
        return all_cases

    def find_test_case_id_by_name(self, name: str) -> Optional[int]:
        """
        Find a test case ID by its display name or pid (case-insensitive exact match).
        Returns the first matching ID or None if not found.
        """
        try:
            cases = self.list_test_cases()
            target = name.strip().lower()
            for c in cases:
                case_name = str(c.get('name', '')).strip().lower()
                case_pid = str(c.get('pid', '')).strip().lower()
                if case_name == target or (case_pid and case_pid == target):
                    return c.get('id') or c.get('test_case_version_id')
            return None
        except Exception as e:
            self.logger.error(f"Failed to find test case by name '{name}': {e}")
            return None

    def find_test_cycle_id_by_name(self, name: str) -> Optional[int]:
        """
        Find a test cycle ID by its name or pid (case-insensitive exact match).
        Returns the first matching ID or None if not found.
        """
        try:
            cycles = self.get_test_cycles() or []
            target = name.strip().lower()
            for cy in cycles:
                cy_name = str(cy.get('name', '')).strip().lower()
                cy_pid = str(cy.get('pid', '')).strip().lower()
                if cy_name == target or (cy_pid and cy_pid == target):
                    return cy.get('id')
            return None
        except Exception as e:
            self.logger.error(f"Failed to find test cycle by name '{name}': {e}")
            return None
