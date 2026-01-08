"""
QTest Robot Framework Library
Provides keywords for integrating QTest with Robot Framework tests
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from qtest_manager import QTestManager
try:
    from robot.api import logger
    from robot.libraries.BuiltIn import BuiltIn
except ImportError:
    # Fallback logger to allow importing this module without Robot Framework installed
    class _FallbackLogger:
        def info(self, msg):
            print(f"INFO: {msg}")
        def debug(self, msg):
            print(f"DEBUG: {msg}")
        def error(self, msg):
            print(f"ERROR: {msg}")
        def warn(self, msg):
            print(f"WARN: {msg}")
    logger = _FallbackLogger()
    BuiltIn = None


class QTestRobotLibrary:
    """Robot Framework library for QTest integration"""
    
    _NOT_INITIALIZED_MSG = "QTest Manager not initialized. Call 'Initialize QTest Manager' first."
    
    def __init__(self):
        """Initialize the library"""
        self.manager = None
        self.test_run_id = None
        self.test_results = []
        self.test_start_times = {}
        
    def initialize_qtest_manager(self, config_path: str = 'config.json'):
        """
        Initialize QTest Manager with configuration
        
        Args:
            config_path: Path to QTest configuration file
            
        Example:
            | Initialize QTest Manager | config.json |
        """
        try:
            self.manager = QTestManager(config_path)
            logger.info(f"QTest Manager initialized with config: {config_path}")
        except Exception as e:
            logger.error(f"Failed to initialize QTest Manager: {str(e)}")
            raise
    
    # -------- Internal helpers (keep public keywords simpler) --------
    def _normalize_tokens(self, test_case_ids) -> List[str]:
        """Normalize provided IDs/names into a list of string tokens."""
        if isinstance(test_case_ids, str):
            return [t.strip() for t in test_case_ids.split(',') if t and t.strip()]
        if isinstance(test_case_ids, (list, tuple)):
            return [str(t).strip() for t in test_case_ids if str(t).strip()]
        return [str(test_case_ids).strip()]

    def _resolve_tokens_to_ids(self, tokens: List[str]) -> Tuple[List[int], List[str]]:
        """Resolve a list of tokens (IDs or names) into integer test case IDs.
        Returns (resolved_ids, missing_names)."""
        resolved_ids: List[int] = []
        missing: List[str] = []
        for tok in tokens:
            # Try integer ID first
            try:
                resolved_ids.append(int(tok))
                continue
            except Exception:
                pass

            # Resolve by name via manager
            try:
                tc_id = self.manager.get_test_case_id_by_name(tok)
            except Exception as e:
                logger.error(f"Error resolving test case '{tok}': {e}")
                tc_id = None
            if tc_id is not None:
                resolved_ids.append(int(tc_id))
            else:
                missing.append(tok)
        return resolved_ids, missing
    
    def create_qtest_test_run(self, name: str, test_case_name,
                              test_cycle_name: Optional[str] = None,
                              description: Optional[str] = None,
                              build_version: Optional[str] = None) -> int:
        """
        Create a new test run in QTest.
        Accepts test case identifiers as IDs or names (or a comma-separated string of either).
        
        Args:
            name: Test run name
            test_case_ids: Test case IDs or names. Can be:
                - list of ints (IDs)
                - list of strings (names or IDs)
                - comma-separated string of names/IDs (e.g. "Login, 12345, Search")
            test_cycle_id: Optional test cycle ID
            description: Optional description
            
        Returns:
            Test run ID
            
        Example:
            | ${test_run_id}= | Create QTest Test Run | My Test Run | 12345,Login,Search |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)
        
        # Normalize provided test_case_name into a list of integer IDs, resolving names when needed
        tokens = self._normalize_tokens(test_case_name)
        resolved_ids, missing = self._resolve_tokens_to_ids(tokens)

        if missing:
            logger.error(f"Could not resolve test case names to IDs: {missing}")
            raise ValueError(f"Unresolved test case names: {missing}")

        if not resolved_ids:
            raise ValueError("No valid test case IDs resolved. Provide IDs or names that exist in qTest.")
        
        testcaseversionid = approve_qtest_test_case(resolved_ids[0])
        try:
            test_run = self.manager.create_test_run(
                name=name,
                test_case_id=resolved_ids[0],
                test_case_version_id=testcaseversionid,
                test_cycle_name=test_cycle_name if test_cycle_name else None,
                description=description,
                build_version=build_version
            )
            self.test_run_id = test_run['id']
            logger.info(f"Test run created: {name} (ID: {self.test_run_id})")
            return self.test_run_id
        except Exception as e:
            logger.error(f"Failed to create test run: {str(e)}")
            raise

    def create_qtest_test_run_by_names(self, name: str, test_case_names, 
                                       test_cycle_name: Optional[str] = None,
                                       description: Optional[str] = None) -> int:
        """
        Create a new test run by passing test case names and optional test cycle name.

        Example:
            | ${run_id}= | Create QTest Test Run By Names | My Run | Login,Register,Search | Regression Cycle |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)

        # Normalize names input
        if isinstance(test_case_names, str):
            test_case_names = [n.strip() for n in test_case_names.split(',') if n.strip()]

        try:
            test_run = self.manager.create_test_run_by_names(
                name=name,
                test_case_names=test_case_names,
                test_cycle_name=test_cycle_name,
                description=description
            )
            self.test_run_id = test_run['id']
            logger.info(f"Test run created by names: {name} (ID: {self.test_run_id})")
            return self.test_run_id
        except Exception as e:
            logger.error(f"Failed to create test run by names: {str(e)}")
            raise
    
    def report_qtest_result(self, test_run_id: int, test_case_id: int, 
                           status: str, steplogs=None,message: str = "",
                           
                           execution_time: int = 0,
                           exe_start_date: Optional[str] = None,
                           exe_end_date: Optional[str] = None):
        """
        Report test result to QTest
        
        Args:
            test_run_id: Test run ID
            test_case_id: Test case ID
            status: Test status (PASSED, FAILED, SKIPPED, etc.)
            message: Optional message/note
            execution_time: Execution time in milliseconds
            
        Example:
            | Report QTest Result | 100 | 12345 | PASSED | Test passed | 3000 |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)
        
        try:
            testcaseversionid = approve_qtest_test_case(test_case_id)
            result = self.manager.update_test_result(
                test_run_id=int(test_run_id),
                test_case_id=int(test_case_id),
                status=status.upper(),
                test_case_version_id=testcaseversionid,
                steplogs=steplogs,
                note=message,
                execution_time=int(execution_time) if execution_time else None,
                exe_start_date=exe_start_date,
                exe_end_date=exe_end_date
            )
            logger.info(f"Test result reported: Test Case {test_case_id} - {status}")
            return result
        except Exception as e:
            logger.error(f"Failed to report test result: {str(e)}")
            # Don't raise - we don't want QTest reporting to fail the test
            return None

    def report_qtest_result_by_name(self, test_run_id: int, test_case_name: str,
                                    status: str, message: str = "",
                                    execution_time: int = 0):
        """
        Report a test result by passing a test case name.

        Example:
            | Report QTest Result By Name | 100 | Login | PASSED | ok | 2500 |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)

        try:
            result = self.manager.update_test_result_by_name(
                test_run_id=int(test_run_id),
                test_case_name=test_case_name,
                status=status.upper(),
                note=message,
                execution_time=int(execution_time) if execution_time else None
            )
            logger.info(f"Test result reported by name: {test_case_name} - {status}")
            return result
        except Exception as e:
            logger.error(f"Failed to report test result by name: {str(e)}")
            return None
    
    def bulk_report_qtest_results(self, test_run_id: int, test_results: List[Dict]):
        """
        Report multiple test results to QTest in bulk
        
        Args:
            test_run_id: Test run ID
            test_results: List of test result dictionaries
            
        Example:
            | ${results}= | Create List | ${result1} | ${result2} |
            | Bulk Report QTest Results | 100 | ${results} |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)
        
        try:
            results = self.manager.bulk_update_test_results(
                test_run_id=int(test_run_id),
                test_results=test_results
            )
            logger.info(f"Bulk test results reported: {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Failed to bulk report test results: {str(e)}")
            return []
    
    def get_qtest_execution_statuses(self) -> List[str]:
        """
        Get available QTest execution statuses
        
        Returns:
            List of available status names
            
        Example:
            | @{statuses}= | Get QTest Execution Statuses |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)
        
        try:
            statuses = self.manager.get_available_statuses()
            logger.info(f"Available statuses: {', '.join(statuses)}")
            return statuses
        except Exception as e:
            logger.error(f"Failed to get execution statuses: {str(e)}")
            return []

    def get_qtest_test_case_id_by_name(self, test_case_name: str) -> int:
        """
        Get a qTest test case ID by providing the test case name.

        Args:
            test_case_name: The exact name of the test case in qTest

        Returns:
            The resolved test case ID

        Example:
            | ${id}= | Get QTest Test Case Id By Name | Login |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)

        cid = self.manager.get_test_case_id_by_name(str(test_case_name))
        if cid is None:
            logger.error(f"Test case not found by name: {test_case_name}")
            raise ValueError(f"Test case not found by name: {test_case_name}")
        logger.info(f"Resolved test case '{test_case_name}' -> ID {cid}")
        return int(cid)
    
    def start_test_timer(self, test_name: str):
        """
        Start timer for a test
        
        Args:
            test_name: Name of the test
            
        Example:
            | Start Test Timer | TC001_Login |
        """
        self.test_start_times[test_name] = time.time()
        logger.debug(f"Timer started for test: {test_name}")
    
    def get_test_duration_ms(self, test_name: str) -> int:
        """
        Get test duration in milliseconds
        
        Args:
            test_name: Name of the test
            
        Returns:
            Duration in milliseconds
            
        Example:
            | ${duration}= | Get Test Duration Ms | TC001_Login |
        """
        if test_name not in self.test_start_times:
            logger.warn(f"No start time found for test: {test_name}")
            return 0
        
        start_time = self.test_start_times[test_name]
        duration_ms = int((time.time() - start_time) * 1000)
        logger.debug(f"Test {test_name} duration: {duration_ms}ms")
        return duration_ms
    
    def finalize_qtest_run(self):
        """
        Finalize QTest test run (cleanup, logging, etc.)
        
        Example:
            | Finalize QTest Run |
        """
        if self.test_run_id:
            logger.info(f"Test run {self.test_run_id} finalized")
            logger.info(f"Total test results recorded: {len(self.test_results)}")
        else:
            logger.warn("No test run was created")
    
    def create_qtest_test_cycle(self, name: str, description: str = "") -> int:
        """
        Create a new test cycle in QTest
        
        Args:
            name: Test cycle name
            description: Optional description
            
        Returns:
            Test cycle ID
            
        Example:
            | ${cycle_id}= | Create QTest Test Cycle | Regression Cycle |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)
        
        try:
            cycle = self.manager.create_test_cycle(
                name=name,
                description=description
            )
            logger.info(f"Test cycle created: {name} (ID: {cycle['id']})")
            return cycle['id']
        except Exception as e:
            logger.error(f"Failed to create test cycle: {str(e)}")
            raise

    def ensure_qtest_test_run_for_case(self,
                                       parent_id,
                                       parent_type: str,
                                       test_case,
                                       create_if_missing: bool = True,
                                       exe_start_date: Optional[str] = None,
                                       exe_end_date: Optional[str] = None) -> int:
        """
        Ensure a test run exists for a given test case under a parent container.

        Args:
            parent_id: ID of the parent container (e.g., test-suite or test-cycle)
            parent_type: Parent type string (e.g., 'test-suite', 'test-cycle')
            test_case: Test case ID or name
            create_if_missing: If true, create the test run when not found
            exe_start_date: Optional execution start date (ISO string)
            exe_end_date: Optional execution end date (ISO string)

        Returns:
            The existing or newly created test run ID

        Example:
            | ${run_id}= | Ensure QTest Test Run For Case | ${suite_id} | test-suite | Login |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)

        # Normalize/convert inputs from Robot
        try:
            pid = int(str(parent_id).strip())
        except Exception:
            raise ValueError(f"Invalid parent_id: {parent_id}")

        tc_id: Optional[int] = None
        # If numeric-like, treat as ID; otherwise resolve by name
        try:
            tc_id = int(str(test_case).strip())
        except Exception:
            tc_id = self.manager.get_test_case_id_by_name(str(test_case))

        if tc_id is None:
            raise ValueError(f"Test case not found: {test_case}")

        run_id = self.manager.ensure_test_run_for_case(
            parent_id=pid,
            parent_type=str(parent_type),
            test_case_id=tc_id,
            create_if_missing=bool(create_if_missing),
            exe_start_date=exe_start_date,
            exe_end_date=exe_end_date
        )
        logger.info(f"Ensured test run for case {tc_id} under {parent_type}:{pid} -> Run ID {run_id}")
        return run_id

    def approve_qtest_test_case(self, test_case) -> int:
        """
        Approve a qTest test case by ID or name and return its version ID.

        Args:
            test_case: Numeric ID or case name.

        Returns:
            Approved test case version ID (int)

        Example:
            | ${version_id}= | Approve QTest Test Case | Login |
            | ${version_id}= | Approve QTest Test Case | 12345 |
        """
        if not self.manager:
            raise RuntimeError(self._NOT_INITIALIZED_MSG)

        # Resolve ID if a name was provided
        tc_id: Optional[int] = None
        try:
            tc_id = int(str(test_case).strip())
        except Exception:
            tc_id = self.manager.get_test_case_id_by_name(str(test_case))
        if tc_id is None:
            raise ValueError(f"Test case not found: {test_case}")

        # Approve the test case
        try:
            self.manager.approve_test_case(tc_id)
            logger.info(f"Approved test case ID {tc_id}")
        except Exception as e:
            logger.error(f"Failed to approve test case {tc_id}: {e}")
            raise

        # Fetch details to retrieve version id
        try:
            details = self.manager.api.get_test_case(tc_id) or {}
            version_id = (
                details.get('test_case_version_id')
                or (details.get('version') or {}).get('id')
            )
            if version_id is None:
                # Fallback: if not present, return the test case id as best-effort
                logger.warn("No explicit version id found; falling back to test case id")
                version_id = tc_id
            return int(version_id)
        except Exception as e:
            logger.error(f"Failed to retrieve version id for test case {tc_id}: {e}")
            # Fallback: return the original ID if details fetch fails
            return int(tc_id)

    def create_qtest_test_step_log(self, testcaseid, step_number, result: str,
                                   actual_result: str = "",
                                   expected_result: Optional[str] = None,
                                   description: Optional[str] = None) -> Dict:
        """
        Create a JSON-serializable dictionary for a qTest test step log by passing step number and result.

        Args:
            step_number: The step order/number (1-based) in the test case.
            result: The step execution result/status (e.g., PASSED, FAILED).
            actual_result: Optional actual result text.
            expected_result: Optional expected result text.
            description: Optional description/notes.

        Returns:
            A dictionary suitable to be included in a test step logs payload.

        Example:
            | ${step}= | Create QTest Test Step Log | 1 | PASSED | Actual ok | Expected ok | Step ran fine |
        """
        # Normalize/validate inputs
        try:
            order = int(str(step_number).strip())
        except Exception:
            raise ValueError(f"Invalid step number: {step_number}")

        status_name = str(result).strip().upper()
        if not status_name:
            raise ValueError("Result/status must be provided for step log")
        statusname_ids={
            'PASSED': 601,
            'FAILED': 602,
            'SKIPPED': 603,
            'BLOCKED': 604
        }
        payload: Dict = {
            # 'order': order,
            'status': { 'id': statusname_ids.get(status_name, 0), 'name': status_name },
            'actual_result': actual_result or ""
        }
        if expected_result is not None:
            payload['expected_result'] = expected_result
        if description is not None:
            payload['description'] = description

        # Try to resolve and append the qTest step ID based on step order and current test case
        try:
            if self.manager:
                # Resolve current test's case ID by its name from Robot context
                if testcaseid:
                    step_id = self.manager.get_test_step_id_by_order(int(testcaseid), order)
                    if step_id is not None:
                        payload['test_step_id'] = int(step_id)
        except Exception as e:
            logger.debug(f"Could not resolve qTest step id for order {order}: {e}")

        logger.debug(f"Created test step log payload: {payload}")
        return payload

    def append_qtest_test_step_log(self, testcaseid, container,
                                   step_number,
                                   result: str,
                                   actual_result: str = "",
                                   expected_result: Optional[str] = None,
                                   description: Optional[str] = None):
        """
        Append a qTest test step log into the provided container (list or dict with 'logs') and return it.
        """
        step = self.create_qtest_test_step_log(
            testcaseid=testcaseid,
            step_number=step_number,
            result=result,
            actual_result=actual_result,
            expected_result=expected_result,
            description=description
        )
        if container is None or container == "":
            return [step]
        if isinstance(container, list):
            container.append(step)
            return container
        if isinstance(container, dict):
            logs = container.get('logs')
            if logs is None:
                logs = []
                container['logs'] = logs
            if not isinstance(logs, list):
                raise ValueError("Expected 'logs' key in dict to be a list")
            logs.append(step)
            return container
        raise ValueError("Container must be a list, a dict (with 'logs'), or empty/None to start a new list")
    
# Instantiate a single library instance for module-level keyword wrappers
_LIB = QTestRobotLibrary()

# Module-level keyword wrappers so Robot Framework can discover keywords when
# importing the library using a file path (e.g., `Library    ../../qtest_robot_library.py`).
def initialize_qtest_manager(config_path: str = 'config.json'):
    return _LIB.initialize_qtest_manager(config_path)

def create_qtest_test_run(name: str, test_case_name, test_cycle_name: Optional[str] = None, description: Optional[str] = None, build_version: Optional[str] = None):
    return _LIB.create_qtest_test_run(name, test_case_name, test_cycle_name, description, build_version)

def create_qtest_test_run_by_names(name: str, test_case_names, test_cycle_name: Optional[str] = None, description: Optional[str] = None):
    return _LIB.create_qtest_test_run_by_names(name, test_case_names, test_cycle_name, description)

def report_qtest_result(test_run_id: int, test_case_id: int, status: str, steplogs, message: str = "", execution_time: int = 0, exe_start_date: Optional[str] = None, exe_end_date: Optional[str] = None):
    return _LIB.report_qtest_result(test_run_id, test_case_id, status, steplogs, message, execution_time, exe_start_date, exe_end_date)
def report_qtest_result_by_name(test_run_id: int, test_case_name: str, status: str, message: str = "", execution_time: int = 0):
    return _LIB.report_qtest_result_by_name(test_run_id, test_case_name, status, message, execution_time)

def bulk_report_qtest_results(test_run_id: int, test_results: List[Dict]):
    return _LIB.bulk_report_qtest_results(test_run_id, test_results)

def get_qtest_execution_statuses() -> List[str]:
    return _LIB.get_qtest_execution_statuses()

def get_qtest_test_case_id_by_name(test_case_name: str) -> int:
    return _LIB.get_qtest_test_case_id_by_name(test_case_name)

def start_test_timer(test_name: str):
    return _LIB.start_test_timer(test_name)

def get_test_duration_ms(test_name: str) -> int:
    return _LIB.get_test_duration_ms(test_name)

def finalize_qtest_run():
    return _LIB.finalize_qtest_run()

def create_qtest_test_cycle(name: str, description: str = "") -> int:
    return _LIB.create_qtest_test_cycle(name, description)

def ensure_qtest_test_run_for_case(parent_id, parent_type: str, test_case, create_if_missing: bool = True, exe_start_date: Optional[str] = None, exe_end_date: Optional[str] = None) -> int:
    return _LIB.ensure_qtest_test_run_for_case(parent_id, parent_type, test_case, create_if_missing, exe_start_date, exe_end_date)

def approve_qtest_test_case(test_case) -> int:
    return _LIB.approve_qtest_test_case(test_case)

def create_qtest_test_step_log(step_number, result: str, actual_result: str = "", expected_result: Optional[str] = None, description: Optional[str] = None) -> Dict:
    return _LIB.create_qtest_test_step_log(step_number, result, actual_result, expected_result, description)

def append_qtest_test_step_log(testcaseid,container, step_number, result: str, actual_result: str = "", expected_result: Optional[str] = None, description: Optional[str] = None):
    return _LIB.append_qtest_test_step_log(testcaseid, container, step_number, result, actual_result, expected_result, description)