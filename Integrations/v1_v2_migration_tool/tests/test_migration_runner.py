#!/usr/bin/env python3
"""
MigrationRunner Integration Tests

Tests for the MigrationRunner class functionality including:
- Subprocess management and execution
- Real-time output streaming
- Process monitoring and control
- Error handling and cleanup
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import tempfile
import shutil
import subprocess
import queue
import threading
import time
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestMigrationRunnerExecution(unittest.TestCase):
    """Test MigrationRunner process execution"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create required file structure
        os.makedirs('src', exist_ok=True)
        with open('v1_v2_component_mappings.json', 'w') as f:
            f.write('[]')
        
        # Create mock phase files
        phase_files = [
            'src/phase1_collect_v1_components.py',
            'src/phase2_collect_v2_components.py',
            'src/phase4a_collect_risk_patterns.py',
            'src/phase4b_transfer_risk_patterns.py'
        ]
        
        for file_path in phase_files:
            with open(file_path, 'w') as f:
                f.write('#!/usr/bin/env python3\nprint("Mock phase script")\n')
        
        # Create main.py
        with open('main.py', 'w') as f:
            f.write('#!/usr/bin/env python3\nprint("Mock main script")\n')
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_migration_runner_initialization(self):
        """Test MigrationRunner proper initialization"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="test.log")
        
        self.assertIsNone(runner.process)
        self.assertIsInstance(runner.output_queue, queue.Queue)
        self.assertFalse(runner.is_running)
        self.assertEqual(runner.log_file, "test.log")
    
    def test_check_prerequisites_all_present(self):
        """Test prerequisites check when all requirements are met"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertEqual(issues, [])
    
    def test_check_prerequisites_missing_mapping_file(self):
        """Test prerequisites check when mapping file is missing"""
        from migration_utils import MigrationRunner
        
        # Remove mapping file
        os.remove('v1_v2_component_mappings.json')
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('v1_v2_component_mappings.json not found' in issue for issue in issues))
    
    def test_check_prerequisites_missing_src_directory(self):
        """Test prerequisites check when src directory is missing"""
        from migration_utils import MigrationRunner
        
        # Remove src directory
        shutil.rmtree('src')
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertTrue(any('src directory not found' in issue for issue in issues))
    
    def test_check_prerequisites_missing_phase_files(self):
        """Test prerequisites check when individual phase files are missing"""
        from migration_utils import MigrationRunner
        
        # Remove one phase file
        os.remove('src/phase1_collect_v1_components.py')
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertTrue(any('phase1_collect_v1_components.py not found' in issue for issue in issues))
    
    @patch('subprocess.Popen')
    def test_start_migration_success(self, mock_popen):
        """Test successful migration start"""
        from migration_utils import MigrationRunner
        
        # Mock process
        mock_process = MagicMock()
        mock_process.stdout.readline.side_effect = [
            b'Starting migration...\n',
            b'Phase 1 complete\n',
            b''  # EOF
        ]
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        success, message = runner.start_migration(test_mode=True)
        
        self.assertTrue(success)
        self.assertIsNotNone(message)
        self.assertTrue(runner.is_running)
        self.assertIsNotNone(runner.process)
        
        # Verify subprocess was called correctly
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        
        # Check command includes Python and main.py
        command = args[0]
        self.assertIn('python', ' '.join(command).lower())
        self.assertIn('main.py', command)
        
        # Check environment has PYTHONUNBUFFERED
        env = kwargs.get('env', {})
        self.assertEqual(env.get('PYTHONUNBUFFERED'), '1')
    
    @patch('subprocess.Popen')
    def test_start_migration_file_not_found(self, mock_popen):
        """Test migration start when main.py doesn't exist"""
        from migration_utils import MigrationRunner
        
        # Remove main.py to cause FileNotFoundError
        if os.path.exists('main.py'):
            os.remove('main.py')
        
        # Mock Popen to raise FileNotFoundError
        mock_popen.side_effect = FileNotFoundError("main.py not found")
        
        runner = MigrationRunner()
        success, message = runner.start_migration()
        
        self.assertFalse(success)
        self.assertFalse(runner.is_running)
        self.assertIn('Error starting migration', message)
    
    @patch('subprocess.Popen')
    def test_start_migration_already_running(self, mock_popen):
        """Test migration start when already running"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        runner.is_running = True  # Simulate already running
        
        success, message = runner.start_migration()
        
        self.assertFalse(success)
        self.assertEqual(message, "Migration is already running")
        
        # Should not start new subprocess
        mock_popen.assert_not_called()
    
    @patch('subprocess.Popen')
    def test_start_migration_subprocess_error(self, mock_popen):
        """Test migration start when subprocess fails"""
        from migration_utils import MigrationRunner
        
        # Mock subprocess failure
        mock_popen.side_effect = subprocess.SubprocessError("Failed to start process")
        
        runner = MigrationRunner()
        success, message = runner.start_migration()
        
        self.assertFalse(success)
        self.assertFalse(runner.is_running)
        self.assertIn("Error starting migration", message)
    
    def test_get_output_lines_empty_queue(self):
        """Test getting output lines when queue is empty"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        lines = runner.get_output_lines()
        
        self.assertEqual(lines, [])
    
    def test_get_output_lines_with_content(self):
        """Test getting output lines when queue has content"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        
        # Manually add items to queue
        runner.output_queue.put("Line 1")
        runner.output_queue.put("Line 2")
        runner.output_queue.put("Line 3")
        
        lines = runner.get_output_lines()
        
        self.assertEqual(lines, ["Line 1", "Line 2", "Line 3"])
        
        # Queue should be empty now
        next_lines = runner.get_output_lines()
        self.assertEqual(next_lines, [])
    
    def test_is_process_running_no_process(self):
        """Test process running check when no process exists"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        
        self.assertFalse(runner.is_process_running())
    
    @patch('subprocess.Popen')
    def test_is_process_running_active_process(self, mock_popen):
        """Test process running check with active process"""
        from migration_utils import MigrationRunner
        
        # Mock active process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        runner.start_migration(test_mode=True)
        
        self.assertTrue(runner.is_process_running())
    
    @patch('subprocess.Popen')
    def test_is_process_running_finished_process(self, mock_popen):
        """Test process running check with finished process"""
        from migration_utils import MigrationRunner
        
        # Mock finished process
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Finished with success
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        runner.start_migration(test_mode=True)
        
        self.assertFalse(runner.is_process_running())
    
    @patch('subprocess.Popen')
    def test_get_process_result_success(self, mock_popen):
        """Test getting process result for successful completion"""
        from migration_utils import MigrationRunner
        
        # Mock successful process
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Success exit code
        mock_process.returncode = 0  # Also set returncode attribute
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        runner.start_migration(test_mode=True)
        
        success, message = runner.get_process_result()
        
        self.assertTrue(success)
        self.assertIsNotNone(message)
        self.assertIn("successfully", message or "")
    
    @patch('subprocess.Popen')
    def test_get_process_result_failure(self, mock_popen):
        """Test getting process result for failed completion"""
        from migration_utils import MigrationRunner
        
        # Mock failed process
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Error exit code
        mock_process.returncode = 1  # Also set returncode attribute
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        runner.start_migration(test_mode=True)
        
        success, message = runner.get_process_result()
        
        self.assertFalse(success)
        self.assertIsNotNone(message)
        self.assertIn("failed", (message or "").lower())
    
    @patch('subprocess.Popen')
    def test_get_process_result_still_running(self, mock_popen):
        """Test getting process result while still running"""
        from migration_utils import MigrationRunner
        
        # Mock running process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process
        
        runner = MigrationRunner()
        runner.start_migration(test_mode=True)
        
        success, message = runner.get_process_result()
        
        self.assertIsNone(success)
        self.assertIsNone(message)
    
    def test_log_to_file_basic(self):
        """Test basic log file writing"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="test.log")
        runner._log_to_file("Test message")
        
        # Verify log file was created and contains message
        self.assertTrue(os.path.exists("test.log"))
        
        with open("test.log", 'r') as f:
            content = f.read()
        
        self.assertIn("Test message", content)
        # Should contain timestamp
        self.assertRegex(content, r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')
    
    def test_log_to_file_multiple_messages(self):
        """Test logging multiple messages"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="multi.log")
        runner._log_to_file("Message 1")
        runner._log_to_file("Message 2")
        runner._log_to_file("Message 3")
        
        with open("multi.log", 'r') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 3)
        
        self.assertIn("Message 1", lines[0])
        self.assertIn("Message 2", lines[1])
        self.assertIn("Message 3", lines[2])
    
    def test_log_to_file_permission_error(self):
        """Test log file writing with permission error"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="/invalid/path/test.log")
        
        # Should not raise exception, but handle gracefully
        try:
            runner._log_to_file("Test message")
        except Exception:
            self.fail("_log_to_file should handle permission errors gracefully")


class TestMigrationRunnerOutputStreaming(unittest.TestCase):
    """Test MigrationRunner real-time output streaming"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_enqueue_output_basic(self):
        """Test basic output enqueuing"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        
        # Mock stdout
        mock_stdout = MagicMock()
        mock_stdout.readline.side_effect = [
            'Line 1\n',
            'Line 2\n',
            ''  # EOF
        ]        # Run enqueue method in thread (simulate real usage)
        thread = threading.Thread(target=runner._enqueue_output, args=(mock_stdout, runner.output_queue))
        thread.daemon = True
        thread.start()
        
        # Give thread time to process
        time.sleep(0.1)
        
        # Check queue has content
        lines = []
        while not runner.output_queue.empty():
            try:
                lines.append(runner.output_queue.get_nowait())
            except queue.Empty:
                break
        
        self.assertIn("Line 1", lines)
        self.assertIn("Line 2", lines)
    
    def test_enqueue_output_unicode_handling(self):
        """Test output enqueuing with unicode characters"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        
        # Mock stdout with unicode
        mock_stdout = MagicMock()
        mock_stdout.readline.side_effect = [
            'Line with émojis 🚀\n',
            'Another line with ñ and ü\n',
            ''  # EOF
        ]
        
        # Run enqueue method
        thread = threading.Thread(target=runner._enqueue_output, args=(mock_stdout, runner.output_queue))
        thread.daemon = True
        thread.start()
        
        time.sleep(0.1)
        
        lines = []
        while not runner.output_queue.empty():
            try:
                lines.append(runner.output_queue.get_nowait())
            except queue.Empty:
                break
        
        # Should properly decode unicode
        line_text = '\n'.join(lines)
        self.assertIn('émojis 🚀', line_text)
        self.assertIn('ñ and ü', line_text)
    
    def test_enqueue_output_error_handling(self):
        """Test output enqueuing with decode errors"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner()
        
        # Mock stdout with problematic content
        mock_stdout = MagicMock()
        mock_stdout.readline.side_effect = [
            'Good line\n',
            'Line with special chars\n',
            'Another good line\n',
            ''  # EOF
        ]
        
        thread = threading.Thread(target=runner._enqueue_output, args=(mock_stdout, runner.output_queue))
        thread.daemon = True
        thread.start()
        
        time.sleep(0.1)
        
        lines = []
        while not runner.output_queue.empty():
            try:
                lines.append(runner.output_queue.get_nowait())
            except queue.Empty:
                break
        
        # Should handle decode errors gracefully
        line_text = '\n'.join(lines)
        self.assertIn('Good line', line_text)
        self.assertIn('Another good line', line_text)


if __name__ == '__main__':
    # Configure test runner for more verbose output
    unittest.main(verbosity=2, buffer=True)