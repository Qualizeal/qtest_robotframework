"""
QTest Manager
High-level manager for QTest operations
"""

import json
import logging
from typing import Dict, List, Optional, Union

from qtest_api import QTestAPI


class QTestManager:
    def get_or_create_test_cycle_id_by_name(self, cycle_name: str, description: str = None) -> int:
        """
        Get a test cycle ID by name, or create it if it does not exist.
        Returns the test cycle ID.
        """
        cycle_id = self.get_test_cycle_id_by_name(cycle_name)
        if cycle_id is not None:
            return cycle_id
        self.logger.info(f"Test cycle '{cycle_name}' not found. Creating new test cycle.")
        created = self.create_test_cycle(name=cycle_name, description=description)
        return created.get('id')
    """High-level manager for QTest operations"""
    
    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize QTest Manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        self.api = QTestAPI(
            base_url=self.config['qtest_url'],
            api_token=self.config['api_token'],
            project_id=self.config['project_id']
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("QTest Manager initialized")
        
        # Cache for execution statuses
        self._execution_statuses = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('qtest_automation.log'),
                logging.StreamHandler()
            ]
        )
    
    def get_execution_statuses(self) -> Dict[str, int]:
        """
        Get execution statuses mapping
        
        Returns:
            Dictionary mapping status names to status IDs
        """
        if self._execution_statuses is None:
            statuses = self.api.get_execution_statuses()
            self._execution_statuses = {
                status['name'].upper(): status['id'] 
                for status in statuses
            }
        return self._execution_statuses
    
    def create_test_run(self, 
                       name: str,
                       test_case_ids: Optional[List[int]] = None,
                       test_case_id: Optional[int] = None,
                       test_case_version_id: Optional[int] = None,
                       description: Optional[str] = None,
                       planned_start_date: Optional[str] = None,
                       planned_end_date: Optional[str] = None,
                       build_version: Optional[str] = None,
                       test_cycle_id: Optional[int] = None,
                       test_cycle_name: Optional[str] = None) -> Dict:
        """
        Create a new test run, or if a test run with the same name exists under the same parent, return its ID and add test cases to it.

        You can specify the parent test cycle by name (test_cycle_name).
        If not provided, the test run is created at the project root.
        """
        self.logger.info(f"Ensuring test run: {name}")
        params_parent_id = None
        params_parent_type = None
        # Prefer explicit ID if provided; else resolve by name
        if test_cycle_id:
            params_parent_id = test_cycle_id
            params_parent_type = 'test-cycle'
        elif test_cycle_name:
            params_parent_id = self.get_or_create_test_cycle_id_by_name(test_cycle_name)
            params_parent_type = 'test-cycle'

        test_run_data = {
            'name': name
        }
        if test_case_id is not None:
            test_run_data['test_case'] = {
                "id": int(test_case_id),
                "test_case_version_id": int(test_case_version_id) if test_case_version_id is not None else None
            }
        if test_case_ids is not None:
            # Some qTest endpoints accept an array; keep compatibility where possible.
            test_run_data['test_case_ids'] = [int(i) for i in test_case_ids]
        if description:
            test_run_data['description'] = description
        if planned_start_date:
            test_run_data['properties'] = test_run_data.get('properties', [])
            test_run_data['properties'].append({
                'field_id': 'PlannedStartDate',
                'field_value': planned_start_date
            })
        if planned_end_date:
            test_run_data['properties'] = test_run_data.get('properties', [])
            test_run_data['properties'].append({
                'field_id': 'PlannedEndDate',
                'field_value': planned_end_date
            })
        if build_version == None:
            # Hard-coded Build Version custom field values as requested
            test_run_data['properties'] = test_run_data.get('properties', [])
            test_run_data['properties'].append({
                'field_id': 12625659,
                'field_name': 'Build Version',
                'field_value': '[3643503]',
                'field_value_name': '[New Value]'
            })
        try:
            result = self.api.create_test_run(test_run_data, parent_id=params_parent_id, parent_type=params_parent_type)
            self.logger.info(f"Test run created successfully. ID: {result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create test run: {str(e)}")
            raise
    
    def update_test_result(self,
                          test_run_id: int,
                          test_case_id: int,
                          status: str,
                          steplogs: [List[Dict]],
                          test_case_version_id: Optional[int] = None,
                          note: Optional[str] = None,
                          execution_time: Optional[int] = None,
                          defects: Optional[List[str]] = None,
                          exe_start_date: Optional[str] = None,
                          exe_end_date: Optional[str] = None) -> Dict:
        """
        Update test case result in a test run
        
        Args:
            test_run_id: Test run ID
            test_case_id: Test case ID
            status: Execution status (PASSED, FAILED, SKIPPED, etc.)
            note: Execution note/comment (optional)
            execution_time: Execution time in milliseconds (optional)
            defects: List of defect IDs (optional)
            attachments: List of attachment file paths (optional)
            
        Returns:
            Created test log details
        """
        self.logger.info(f"Updating test result for test case {test_case_id} in run {test_run_id}")
        
        # Get status ID from status name
        statuses = self.get_execution_statuses()
        status_upper = status.upper()
        
        if status_upper not in statuses:
            raise ValueError(f"Invalid status: {status}. Available statuses: {list(statuses.keys())}")
        
        status_id = statuses[status_upper]
        
        test_log_data = {
            'status': {
                'id': status_id,
                'name': status_upper
            },
            'test_case_version_id': test_case_version_id if test_case_version_id is not None else test_case_id
        }
        
        if note:
            test_log_data['note'] = note
        
        if execution_time:
            test_log_data['exe_time'] = execution_time
        
        if defects:
            test_log_data['defects'] = [{'id': defect_id} for defect_id in defects]
        if exe_start_date:
            test_log_data['exe_start_date'] = exe_start_date
        if exe_end_date:
            test_log_data['exe_end_date'] = exe_end_date
        test_log_data['test_step_logs'] = steplogs['logs']
        try:
            result = self.api.add_test_log(test_run_id, test_log_data)
            self.logger.info(f"Test result updated successfully. Test log ID: {result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to update test result: {str(e)}")
            raise
    
    def bulk_update_test_results(self, 
                                test_run_id: int,
                                test_results: List[Dict]) -> List[Dict]:
        """
        Update multiple test results in a test run
        
        Args:
            test_run_id: Test run ID
            test_results: List of test result dictionaries with keys:
                         'test_case_id', 'status', 'note' (optional)
            
        Returns:
            List of created test log details
        """
        self.logger.info(f"Bulk updating {len(test_results)} test results")
        
        results = []
        for test_result in test_results:
            try:
                result = self.update_test_result(
                    test_run_id=test_run_id,
                    test_case_id=test_result['test_case_id'],
                    status=test_result['status'],
                    note=test_result.get('note'),
                    execution_time=test_result.get('execution_time'),
                    defects=test_result.get('defects')
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to update test case {test_result['test_case_id']}: {str(e)}")
                results.append({'error': str(e), 'test_case_id': test_result['test_case_id']})
        
        self.logger.info(f"Bulk update completed. {len([r for r in results if 'error' not in r])} successful")
        return results
    
    def get_test_run_results(self, test_run_id: int) -> List[Dict]:
        """
        Get all test results from a test run
        
        Args:
            test_run_id: Test run ID
            
        Returns:
            List of test log details
        """
        self.logger.info(f"Fetching test results for test run {test_run_id}")
        
        try:
            results = self.api.get_test_logs(test_run_id)
            self.logger.info(f"Retrieved {len(results)} test results")
            return results
        except Exception as e:
            self.logger.error(f"Failed to get test results: {str(e)}")
            raise
    
    def create_test_cycle(self,
                         name: str,
                         description: Optional[str] = None,
                         parent_id: Optional[int] = None) -> Dict:
        """
        Create a new test cycle
        
        Args:
            name: Test cycle name
            description: Test cycle description (optional)
            parent_id: Parent test cycle ID (optional, for nested cycles)
            
        Returns:
            Created test cycle details
        """
        self.logger.info(f"Creating test cycle: {name}")
        
        test_cycle_data = {
            'name': name
        }
        
        if description:
            test_cycle_data['description'] = description
        
        if parent_id:
            test_cycle_data['parent_id'] = parent_id
        
        try:
            result = self.api.create_test_cycle(test_cycle_data)
            self.logger.info(f"Test cycle created successfully. ID: {result.get('id')}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to create test cycle: {str(e)}")
            raise
    
    def get_available_statuses(self) -> List[str]:
        """Get list of available execution status names"""
        return list(self.get_execution_statuses().keys())

    # -------- Name-based operations --------
    def get_test_cycle_id_by_name(self, cycle_name: str) -> Optional[int]:
        """
        Resolve a test cycle ID by its name.
        Returns None if not found.
        """
        self.logger.debug(f"Resolving test cycle ID for name: {cycle_name}")
        return self.api.find_test_cycle_id_by_name(cycle_name)

    def get_test_case_id_by_name(self, case_name: str) -> Optional[int]:
        """
        Resolve a test case ID by its name.
        Returns None if not found.
        """
        self.logger.debug(f"Resolving test case ID for name: {case_name}")
        return self.api.find_test_case_id_by_name(case_name)

    def resolve_test_case_ids_by_names(self, test_case_names: List[str]) -> List[int]:
        """Resolve multiple test case names to IDs (ignoring names not found)."""
        resolved: List[int] = []
        missing: List[str] = []
        for name in test_case_names:
            cid = self.get_test_case_id_by_name(name)
            if cid:
                resolved.append(cid)
            else:
                missing.append(name)
        if missing:
            self.logger.warning(f"Could not resolve test cases: {missing}")
        return resolved

    def create_test_run_by_names(self,
                                 name: str,
                                 test_case_names: List[str],
                                 test_cycle_name: Optional[str] = None,
                                 description: Optional[str] = None,
                                 planned_start_date: Optional[str] = None,
                                 planned_end_date: Optional[str] = None,
                                 build_version: Optional[str] = None) -> Dict:
        """
        Create a new test run by passing test case names and optional test cycle name.
        """
        cycle_id = None
        if test_cycle_name:
            cycle_id = self.get_test_cycle_id_by_name(test_cycle_name)
            if cycle_id is None:
                self.logger.warning(f"Test cycle '{test_cycle_name}' not found; creating without parent.")
        case_ids = self.resolve_test_case_ids_by_names(test_case_names)
        if not case_ids:
            raise ValueError("No test cases resolved. Please verify names.")
        return self.create_test_run(
            name=name,
            test_case_ids=case_ids,
            test_cycle_name=test_cycle_name,
            description=description,
            planned_start_date=planned_start_date,
            planned_end_date=planned_end_date,
            build_version=build_version
        )

    def update_test_result_by_name(self,
                                   test_run_id: int,
                                   test_case_name: str,
                                   
                                   status: str,
                                   test_case_version_id: Optional[int] = None,
                                   note: Optional[str] = None,
                                   execution_time: Optional[int] = None,
                                   defects: Optional[List[str]] = None) -> Dict:
        """Update a test result by resolving the test case name to its ID."""
        cid = self.get_test_case_id_by_name(test_case_name)
        if cid is None:
            raise ValueError(f"Test case not found by name: {test_case_name}")
        return self.update_test_result(
            test_run_id=test_run_id,
            test_case_id=cid,
            test_case_version_id=None,
            status=status,
            note=note,
            execution_time=execution_time,
            defects=defects
        )

    # -------- Approve test case --------
    def approve_test_case(self, test_case_id: int) -> Dict:
        """
        Approve a test case version by ID.
        """
        self.logger.info(f"Approving test case ID: {test_case_id}")
        return self.api.approve_test_case(int(test_case_id))

    def approve_test_case_by_name(self, case_name: str) -> Dict:
        """
        Approve a test case version by resolving its name to ID.
        """
        cid = self.get_test_case_id_by_name(case_name)
        if cid is None:
            raise ValueError(f"Test case not found by name: {case_name}")
        return self.approve_test_case(cid)

    # -------- Ensure test run exists for a test case --------
    def ensure_test_run_for_case(self,
                                 parent_id: int,
                                 parent_type: str,
                                 test_case_id: int,
                                 create_if_missing: bool = True,
                                 exe_start_date: Optional[str] = None,
                                 exe_end_date: Optional[str] = None) -> int:
        """
        Ensure a test run exists for the given test case under a parent (e.g., test-suite).
        If found, returns the existing test run ID. Otherwise, creates it (if allowed) and returns its ID.
        """
        self.logger.info(f"Ensuring test run for case {test_case_id} under {parent_type}:{parent_id}")
        existing_id = self.api.find_test_run_id_by_test_case(parent_id, parent_type, test_case_id)
        if existing_id:
            self.logger.info(f"Found existing test run {existing_id} for test case {test_case_id}")
            return int(existing_id)
        if not create_if_missing:
            raise ValueError(f"No test run found for test case {test_case_id} under {parent_type}:{parent_id}")
        created = self.api.create_test_run_for_case(
            parent_id=parent_id,
            parent_type=parent_type,
            test_case_id=test_case_id,
            exe_start_date=exe_start_date,
            exe_end_date=exe_end_date
        )
        run_id = created.get('id')
        self.logger.info(f"Created new test run {run_id} for test case {test_case_id}")
        return int(run_id)

    # -------- Test step helpers --------
    def get_test_step_id_by_order(self, test_case_id: int, step_number: int) -> Optional[int]:
        """
        Return the test step ID for the given test case by step order/number.
        """
        self.logger.debug(f"Resolving step id for test case {test_case_id} order {step_number}")
        try:
            return self.api.find_test_step_id_by_order(int(test_case_id), int(step_number))
        except Exception as e:
            self.logger.error(f"Failed to get step id for case {test_case_id} order {step_number}: {e}")
            return None

    def get_test_step_id_by_name(self, test_case_id: int, step_name: str) -> Optional[int]:
        """
        Return the test step ID by matching name/description fields.
        Matches against 'name', 'description', or 'action' fields case-insensitively.
        """
        try:
            steps = self.api.get_test_steps(int(test_case_id)) or []
            target = str(step_name).strip().lower()
            for s in steps:
                candidates = [
                    str(s.get('name', '')).strip().lower(),
                    str(s.get('description', '')).strip().lower(),
                    str(s.get('action', '')).strip().lower(),
                ]
                if target and target in candidates:
                    return s.get('id')
            return None
        except Exception as e:
            self.logger.error(f"Failed to get step id by name for case {test_case_id}: {e}")
            return None
