#!/usr/bin/env python3
"""
Streamlit App Tests

Tests for the Streamlit web interface functionality including:
- Migration runner functionality
- Configuration handling
- File operations and validation
- Log handling
- Migration summary generation
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import tempfile
import shutil
from pathlib import Path
import json
import subprocess
import queue
import threading

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMigrationRunnerCore(unittest.TestCase):
    """Test MigrationRunner core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_migration_runner_initialization(self):
        """Test MigrationRunner initialization"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="test.log")
        
        self.assertIsNone(runner.process)
        self.assertIsInstance(runner.output_queue, queue.Queue)
        self.assertFalse(runner.is_running)
        self.assertEqual(runner.log_file, "test.log")
    
    def test_env_variables_save_and_load(self):
        """Test saving and loading environment variables"""
        from migration_utils import save_env_variables, load_env_variables
        
        api_token = 'test-api-token-123'
        subdomain = 'test-subdomain'
        
        # Save variables
        save_env_variables(api_token, subdomain)
        
        # Verify .env file was created
        self.assertTrue(os.path.exists('.env'))
        
        # Load variables back
        loaded_token, loaded_subdomain = load_env_variables()
        
        self.assertEqual(loaded_token, 'test-api-token-123')
        self.assertEqual(loaded_subdomain, 'test-subdomain')
    
    def test_env_variables_special_characters(self):
        """Test environment variables with special characters"""
        from migration_utils import save_env_variables, load_env_variables
        
        api_token = 'token!@#$%^&*()_+-='
        subdomain = 'test-sub.domain-name'
        
        save_env_variables(api_token, subdomain)
        loaded_token, loaded_subdomain = load_env_variables()
        
        self.assertEqual(loaded_token, 'token!@#$%^&*()_+-=')
        self.assertEqual(loaded_subdomain, 'test-sub.domain-name')
    
    def test_env_variables_missing_file(self):
        """Test loading environment variables when .env file doesn't exist"""
        from migration_utils import load_env_variables
        
        # Ensure no .env file exists
        if os.path.exists('.env'):
            os.remove('.env')
        
        loaded_token, loaded_subdomain = load_env_variables()
        
        # Should return empty strings when file doesn't exist
        self.assertEqual(loaded_token, '')
        self.assertEqual(loaded_subdomain, '')
    
    def test_env_variables_empty_values(self):
        """Test handling of empty environment variable values"""
        from migration_utils import save_env_variables, load_env_variables
        
        api_token = ''
        subdomain = 'test-subdomain'
        
        save_env_variables(api_token, subdomain)
        loaded_token, loaded_subdomain = load_env_variables()
        
        self.assertEqual(loaded_token, '')
        self.assertEqual(loaded_subdomain, 'test-subdomain')
    
    def test_env_file_content_format(self):
        """Test that .env file is formatted correctly"""
        from migration_utils import save_env_variables
        
        api_token = 'test-token-abc123'
        subdomain = 'my-company'
        
        save_env_variables(api_token, subdomain)
        
        # Verify file contents
        with open('.env', 'r') as f:
            content = f.read()
        
        expected_content = "API_TOKEN=test-token-abc123\nSUBDOMAIN=my-company\n"
        self.assertEqual(content, expected_content)


class TestStreamlitValidation(unittest.TestCase):
    """Test validation logic in Streamlit app"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create basic file structure
        os.makedirs('src', exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_prerequisites_check_all_present(self):
        """Test prerequisites check when all files are present"""
        from migration_utils import MigrationRunner
        
        # Create required files
        with open('v1_v2_component_mappings.json', 'w') as f:
            json.dump([], f)
        
        required_files = [
            'src/phase1_collect_v1_components.py',
            'src/phase2_collect_v2_components.py', 
            'src/phase4a_collect_risk_patterns.py',
            'src/phase4b_transfer_risk_patterns.py'
        ]
        
        for file_path in required_files:
            with open(file_path, 'w') as f:
                f.write('# Test file')
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertEqual(issues, [])
    
    def test_prerequisites_check_missing_files(self):
        """Test prerequisites check when files are missing"""
        from migration_utils import MigrationRunner
        
        # Don't create any files
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        # Should have multiple issues
        self.assertGreater(len(issues), 0)
        
        # Check specific expected issues
        self.assertTrue(any('v1_v2_component_mappings.json not found' in issue for issue in issues))
        self.assertTrue(any('phase1_collect_v1_components.py not found' in issue for issue in issues))
    
    def test_prerequisites_check_missing_src_directory(self):
        """Test prerequisites check when src directory is missing"""
        from migration_utils import MigrationRunner
        
        # Create mapping file but remove src directory
        with open('v1_v2_component_mappings.json', 'w') as f:
            json.dump([], f)
        
        if os.path.exists('src'):
            shutil.rmtree('src')
        
        runner = MigrationRunner()
        issues = runner.check_prerequisites()
        
        self.assertTrue(any('src directory not found' in issue for issue in issues))
    
    def test_validate_configuration_complete(self):
        """Test validation of complete configuration"""
        # This would test configuration validation logic
        # For now, we'll create a conceptual test
        
        config = {
            'BASE_URL': 'https://test.iriusrisk.com',
            'USERNAME': 'testuser',
            'PASSWORD': 'testpass123',
            'MAX_REQUESTS_PER_SECOND': '5.0'
        }
        
        def validate_config(config):
            errors = []
            if not config.get('BASE_URL'):
                errors.append('BASE_URL is required')
            if not config.get('USERNAME'):
                errors.append('USERNAME is required')
            if not config.get('PASSWORD'):
                errors.append('PASSWORD is required')
            return errors
        
        errors = validate_config(config)
        self.assertEqual(errors, [])
    
    def test_validate_configuration_missing_fields(self):
        """Test validation of incomplete configuration"""
        config = {
            'BASE_URL': 'https://test.iriusrisk.com',
            'USERNAME': '',  # Missing
            'PASSWORD': 'testpass123',
            'MAX_REQUESTS_PER_SECOND': '5.0'
        }
        
        def validate_config(config):
            errors = []
            if not config.get('BASE_URL'):
                errors.append('BASE_URL is required')
            if not config.get('USERNAME'):
                errors.append('USERNAME is required')
            if not config.get('PASSWORD'):
                errors.append('PASSWORD is required')
            return errors
        
        errors = validate_config(config)
        self.assertIn('USERNAME is required', errors)


class TestStreamlitLogHandling(unittest.TestCase):
    """Test log handling functionality in Streamlit app"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_migration_runner_logging(self):
        """Test MigrationRunner log file creation"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="test_migration.log")
        runner._log_to_file("Test log message")
        
        # Verify log file was created
        self.assertTrue(os.path.exists("test_migration.log"))
        
        # Verify content
        with open("test_migration.log", 'r') as f:
            content = f.read()
        
        self.assertIn("Test log message", content)
        self.assertIn("[202", content)  # Should contain timestamp
    
    def test_migration_runner_log_multiple_messages(self):
        """Test multiple log messages are appended"""
        from migration_utils import MigrationRunner
        
        runner = MigrationRunner(log_file="test_multi.log")
        runner._log_to_file("Message 1")
        runner._log_to_file("Message 2")
        runner._log_to_file("Message 3")
        
        with open("test_multi.log", 'r') as f:
            content = f.read()
        
        self.assertIn("Message 1", content)
        self.assertIn("Message 2", content)
        self.assertIn("Message 3", content)
        
        # Verify they're on separate lines
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 3)
    
    def test_migration_runner_log_file_permissions(self):
        """Test handling of log file permission errors"""
        from migration_utils import MigrationRunner
        
        # Create runner with log file in non-existent directory
        # This should be handled gracefully
        runner = MigrationRunner(log_file="/non/existent/path/test.log")
        
        # Should not raise exception
        try:
            runner._log_to_file("Test message")
        except Exception:
            self.fail("_log_to_file() should handle permission errors gracefully")


class TestStreamlitMigrationSummary(unittest.TestCase):
    """Test migration summary functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_get_migration_summary_with_results(self):
        """Test migration summary generation with result files"""
        from migration_utils import get_migration_summary
        
        # Create mock result files
        test_v1_components = [{'id': 'comp1'}, {'id': 'comp2'}]
        test_v2_components = [{'id': 'comp3'}, {'id': 'comp4'}, {'id': 'comp5'}]
        test_results = {'successful_transfers': 5, 'failed_transfers': 1}
        
        with open('v1_components.json', 'w') as f:
            json.dump(test_v1_components, f)
        with open('v2_components.json', 'w') as f:
            json.dump(test_v2_components, f)
        with open('phase4b_transfer_results.json', 'w') as f:
            json.dump(test_results, f)
        
        summary = get_migration_summary()
        
        self.assertIsNotNone(summary)
        self.assertIsInstance(summary, list)
        self.assertGreater(len(summary), 0)
        
        # Check that summary contains expected items
        summary_str = '\n'.join(summary)
        self.assertIn('V1 (deprecated) components: 2 items', summary_str)
        self.assertIn('V2 (modern) components: 3 items', summary_str)
        self.assertIn('Transfer results:', summary_str)
    
    def test_get_migration_summary_no_results(self):
        """Test migration summary when no result files exist"""
        from migration_utils import get_migration_summary
        
        # Don't create any result files
        
        summary = get_migration_summary()
        
        # Should return list with "Not found" messages when no files exist
        self.assertIsInstance(summary, list)
        self.assertEqual(len(summary), 6)  # 6 files checked
        
        # All should be "Not found"
        summary_str = '\n'.join(summary)
        self.assertIn('Not found', summary_str)
    
    def test_get_migration_summary_invalid_json(self):
        """Test migration summary with corrupted result file"""
        from migration_utils import get_migration_summary
        
        # Create invalid JSON file
        with open('phase4b_transfer_results.json', 'w') as f:
            f.write('invalid json content')
        
        summary = get_migration_summary()
        
        # Should handle invalid JSON gracefully
        self.assertIsInstance(summary, list)
        
        # Should contain warning about unreadable file
        summary_str = '\n'.join(summary)
        self.assertIn('couldn\'t read details', summary_str)


if __name__ == '__main__':
    # Configure test runner for more verbose output
    unittest.main(verbosity=2, buffer=True)