#!/usr/bin/env python3
"""
Unit Tests for Radiant Swing

Comprehensive unit tests for individual functions in each phase.
Each test is isolated and tests specific functionality with various edge cases.
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
import requests
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPhase1Units(unittest.TestCase):
    """Unit tests for Phase 1 individual functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    @patch.dict(os.environ, {'API_TOKEN': 'test-token-123', 'SUBDOMAIN': 'test-sub'})
    def test_get_api_config_with_env_vars(self):
        """Test get_api_config with environment variables"""
        import phase1_collect_v1_components as phase1
        
        headers, base_url = phase1.get_api_config()
        
        self.assertIn('Accept', headers)
        self.assertIn('api-token', headers)
        self.assertEqual(headers['api-token'], 'test-token-123')
        self.assertEqual(base_url, 'https://test-sub.iriusrisk.com/api/v2')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_config_with_defaults(self):
        """Test get_api_config with default values when env vars missing"""
        import phase1_collect_v1_components as phase1
        
        headers, base_url = phase1.get_api_config()
        
        # Should use defaults
        self.assertEqual(headers['api-token'], '930f391d-85fc-4461-a860-ae28485b5ec9')
        self.assertEqual(base_url, 'https://r2.iriusrisk.com/api/v2')
    
    def test_save_to_json_success(self):
        """Test successful JSON file saving"""
        import phase1_collect_v1_components as phase1
        
        test_data = [
            {'id': 'comp1', 'name': 'Component 1'},
            {'id': 'comp2', 'name': 'Component 2'}
        ]
        filename = 'test_output.json'
        
        result = phase1.save_to_json(test_data, filename)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        with open(filename, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_data)
    
    def test_save_to_json_empty_list(self):
        """Test saving empty list to JSON"""
        import phase1_collect_v1_components as phase1
        
        result = phase1.save_to_json([], 'empty.json')
        
        self.assertTrue(result)
        with open('empty.json', 'r') as f:
            data = json.load(f)
        self.assertEqual(data, [])
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_save_to_json_permission_error(self, mock_open):
        """Test JSON saving with permission error"""
        import phase1_collect_v1_components as phase1
        
        result = phase1.save_to_json([{'test': 'data'}], 'readonly.json')
        
        self.assertFalse(result)
    
    @patch('phase1_collect_v1_components.requests.get')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_collect_v1_components_success(self, mock_get):
        """Test successful component collection"""
        import phase1_collect_v1_components as phase1
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            '_embedded': {
                'items': [
                    {'id': 'comp1', 'name': 'Deprecated Component 1', 'referenceId': 'ref1'},
                    {'id': 'comp2', 'name': 'Regular Component', 'referenceId': 'ref2'}
                ]
            },
            'page': {'totalElements': 2, 'size': 2000}
        }
        mock_get.return_value = mock_response
        
        components = phase1.collect_v1_components()
        
        self.assertEqual(len(components), 2)
        self.assertEqual(components[0]['name'], 'Deprecated Component 1')
        mock_get.assert_called_once()
    
    @patch('phase1_collect_v1_components.requests.get')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_collect_v1_components_empty_response(self, mock_get):
        """Test component collection with empty API response"""
        import phase1_collect_v1_components as phase1
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            '_embedded': {'items': []},
            'page': {'totalElements': 0}
        }
        mock_get.return_value = mock_response
        
        components = phase1.collect_v1_components()
        
        self.assertEqual(components, [])
    
    @patch('phase1_collect_v1_components.requests.get')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_collect_v1_components_api_error(self, mock_get):
        """Test component collection with API error"""
        import phase1_collect_v1_components as phase1
        
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        components = phase1.collect_v1_components()
        
        self.assertEqual(components, [])
    
    @patch('phase1_collect_v1_components.requests.get')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_collect_v1_components_invalid_json(self, mock_get):
        """Test component collection with invalid JSON response"""
        import phase1_collect_v1_components as phase1
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response
        
        components = phase1.collect_v1_components()
        
        self.assertEqual(components, [])


class TestPhase2Units(unittest.TestCase):
    """Unit tests for Phase 2 individual functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_filter_v2_components_basic(self):
        """Test basic filtering of deprecated components"""
        import phase2_collect_v2_components as phase2
        
        all_components = [
            {'id': 'comp1', 'name': 'Modern Component', 'referenceId': 'ref1'},
            {'id': 'comp2', 'name': 'Deprecated Component', 'referenceId': 'ref2'},
            {'id': 'comp3', 'name': 'Another Component', 'referenceId': 'ref3'},
            {'id': 'comp4', 'name': 'Test deprecated item', 'referenceId': 'ref4'}
        ]
        
        v2_components = phase2.filter_v2_components(all_components)
        
        # Should filter out deprecated components (case insensitive)
        self.assertEqual(len(v2_components), 2)
        names = [comp['name'] for comp in v2_components]
        self.assertIn('Modern Component', names)
        self.assertIn('Another Component', names)
        self.assertNotIn('Deprecated Component', names)
        self.assertNotIn('Test deprecated item', names)
    
    def test_filter_v2_components_empty_list(self):
        """Test filtering empty component list"""
        import phase2_collect_v2_components as phase2
        
        v2_components = phase2.filter_v2_components([])
        
        self.assertEqual(v2_components, [])
    
    def test_filter_v2_components_all_deprecated(self):
        """Test filtering when all components are deprecated"""
        import phase2_collect_v2_components as phase2
        
        all_components = [
            {'id': 'comp1', 'name': 'Deprecated Component 1', 'referenceId': 'ref1'},
            {'id': 'comp2', 'name': 'Another Deprecated Item', 'referenceId': 'ref2'}
        ]
        
        v2_components = phase2.filter_v2_components(all_components)
        
        self.assertEqual(v2_components, [])
    
    def test_filter_v2_components_none_deprecated(self):
        """Test filtering when no components are deprecated"""
        import phase2_collect_v2_components as phase2
        
        all_components = [
            {'id': 'comp1', 'name': 'Modern Component 1', 'referenceId': 'ref1'},
            {'id': 'comp2', 'name': 'Current Component 2', 'referenceId': 'ref2'}
        ]
        
        v2_components = phase2.filter_v2_components(all_components)
        
        self.assertEqual(len(v2_components), 2)
    
    def test_filter_v2_components_edge_cases(self):
        """Test filtering with edge cases in component names"""
        import phase2_collect_v2_components as phase2
        
        all_components = [
            {'id': 'comp1', 'name': 'Component with DEPRECATED in caps', 'referenceId': 'ref1'},
            {'id': 'comp2', 'name': 'Undeprecated Component', 'referenceId': 'ref2'},  # Contains 'deprecated' but not flagged
            {'id': 'comp3', 'name': '', 'referenceId': 'ref3'},  # Empty name
            {'id': 'comp4', 'name': 'deprecated', 'referenceId': 'ref4'}  # Just 'deprecated'
        ]
        
        v2_components = phase2.filter_v2_components(all_components)
        
        # Should filter out components 1 and 4, keep 2 and 3
        self.assertEqual(len(v2_components), 2)
        names = [comp['name'] for comp in v2_components]
        self.assertIn('Undeprecated Component', names)
        self.assertIn('', names)


class TestPhase4aUnits(unittest.TestCase):
    """Unit tests for Phase 4a individual functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_load_mappings_success(self):
        """Test successful mapping loading"""
        import phase4a_collect_risk_patterns as phase4a
        
        test_mappings = [
            {
                'v1_component': {'id': 'v1-1', 'name': 'Old Comp 1'},
                'v2_component': {'id': 'v2-1', 'name': 'New Comp 1'},
                'mapping_status': 'MATCHED'
            },
            {
                'v1_component': {'id': 'v1-2', 'name': 'Old Comp 2'},
                'v2_component': None,
                'mapping_status': 'NO_MATCH'
            },
            {
                'v1_component': {'id': 'v1-3', 'name': 'Old Comp 3'},
                'v2_component': {'id': 'v2-3', 'name': 'New Comp 3'},
                'mapping_status': 'MATCHED'
            }
        ]
        
        with open('v1_v2_component_mappings.json', 'w') as f:
            json.dump(test_mappings, f)
        
        mappings = phase4a.load_mappings()
        
        # Should only return MATCHED mappings with v2_component
        self.assertEqual(len(mappings), 2)
        for mapping in mappings:
            self.assertEqual(mapping['mapping_status'], 'MATCHED')
            self.assertIsNotNone(mapping['v2_component'])
    
    def test_load_mappings_file_not_found(self):
        """Test loading mappings when file doesn't exist"""
        import phase4a_collect_risk_patterns as phase4a
        
        mappings = phase4a.load_mappings()
        
        self.assertEqual(mappings, [])
    
    def test_load_mappings_invalid_json(self):
        """Test loading mappings with invalid JSON"""
        import phase4a_collect_risk_patterns as phase4a
        
        with open('v1_v2_component_mappings.json', 'w') as f:
            f.write('invalid json content')
        
        mappings = phase4a.load_mappings()
        
        self.assertEqual(mappings, [])
    
    def test_load_component_ids_success(self):
        """Test successful component ID loading"""
        import phase4a_collect_risk_patterns as phase4a
        
        v1_components = [
            {'id': 'uuid-v1-1', 'referenceId': 'ref-v1-1', 'name': 'V1 Comp 1'},
            {'id': 'uuid-v1-2', 'referenceId': 'ref-v1-2', 'name': 'V1 Comp 2'}
        ]
        
        v2_components = [
            {'id': 'uuid-v2-1', 'referenceId': 'ref-v2-1', 'name': 'V2 Comp 1'},
            {'id': 'uuid-v2-2', 'referenceId': 'ref-v2-2', 'name': 'V2 Comp 2'}
        ]
        
        with open('v1_components.json', 'w') as f:
            json.dump(v1_components, f)
        with open('v2_components.json', 'w') as f:
            json.dump(v2_components, f)
        
        component_lookup = phase4a.load_component_ids()
        
        self.assertIn('ref-v1-1', component_lookup)
        self.assertIn('ref-v2-2', component_lookup)
        self.assertEqual(component_lookup['ref-v1-1']['id'], 'uuid-v1-1')
        self.assertEqual(component_lookup['ref-v2-2']['id'], 'uuid-v2-2')
        self.assertEqual(len(component_lookup), 4)
    
    def test_load_component_ids_missing_files(self):
        """Test component ID loading when files are missing"""
        import phase4a_collect_risk_patterns as phase4a
        
        component_lookup = phase4a.load_component_ids()
        
        self.assertEqual(component_lookup, {})
    
    def test_find_component_risk_patterns_found(self):
        """Test finding risk patterns for a component"""
        import phase4a_collect_risk_patterns as phase4a
        
        component_lookup = {
            'ref-comp-1': {'id': 'uuid-comp-1', 'name': 'Component 1', 'type': 'v1'},
            'ref-comp-2': {'id': 'uuid-comp-2', 'name': 'Component 2', 'type': 'v2'}
        }
        
        # Mock the API call
        with patch('phase4a_collect_risk_patterns.get_component_risk_patterns_direct') as mock_api:
            mock_api.return_value = [
                {'id': 'rp-1', 'name': 'Risk Pattern 1'},
                {'id': 'rp-2', 'name': 'Risk Pattern 2'}
            ]
            
            risk_patterns = phase4a.find_component_risk_patterns('ref-comp-1', component_lookup)
            
            self.assertEqual(len(risk_patterns), 2)
            self.assertEqual(risk_patterns[0]['name'], 'Risk Pattern 1')
            mock_api.assert_called_once_with('uuid-comp-1')
    
    def test_find_component_risk_patterns_not_found(self):
        """Test finding risk patterns for component not in lookup"""
        import phase4a_collect_risk_patterns as phase4a
        
        component_lookup = {'ref-comp-1': 'uuid-comp-1'}
        
        risk_patterns = phase4a.find_component_risk_patterns('ref-nonexistent', component_lookup)
        
        self.assertEqual(risk_patterns, [])


class TestPhase4bUnits(unittest.TestCase):
    """Unit tests for Phase 4b individual functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_load_risk_pattern_mappings_success(self):
        """Test successful risk pattern mapping loading"""
        import phase4b_transfer_risk_patterns as phase4b
        
        test_mappings = [
            {
                'v1_component': {'id': 'v1-1', 'name': 'Old Comp 1'},
                'v2_component': {'id': 'v2-1', 'name': 'New Comp 1'},
                'risk_patterns': [
                    {'id': 'rp-1', 'name': 'Risk Pattern 1'}
                ],
                'risk_patterns_count': 1
            },
            {
                'v1_component': {'id': 'v1-2', 'name': 'Old Comp 2'},
                'v2_component': {'id': 'v2-2', 'name': 'New Comp 2'},
                'risk_patterns': [],  # No risk patterns
                'risk_patterns_count': 0
            }
        ]
        
        with open('matching_risk_patterns.json', 'w') as f:
            json.dump(test_mappings, f)
        
        mappings = phase4b.load_risk_pattern_mappings()
        
        # Should only return mappings with risk patterns
        self.assertEqual(len(mappings), 1)
        self.assertEqual(len(mappings[0]['risk_patterns']), 1)
    
    @patch('phase4b_transfer_risk_patterns.requests.post')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_add_risk_pattern_success(self, mock_post):
        """Test successful risk pattern addition"""
        import phase4b_transfer_risk_patterns as phase4b
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'success': True}
        mock_post.return_value = mock_response
        
        logger = MagicMock()
        
        result = phase4b.add_risk_pattern_to_component(
            'v1-component-id',
            'risk-pattern-id',
            'Test Risk Pattern',
            logger
        )
        
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify the API call was made with correct payload
        args, kwargs = mock_post.call_args
        self.assertIn('json', kwargs)
        payload = kwargs['json']
        self.assertEqual(payload['riskPattern']['id'], 'risk-pattern-id')
    
    @patch('phase4b_transfer_risk_patterns.requests.post')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_add_risk_pattern_failure(self, mock_post):
        """Test risk pattern addition failure"""
        import phase4b_transfer_risk_patterns as phase4b
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        logger = MagicMock()
        
        result = phase4b.add_risk_pattern_to_component(
            'v1-component-id',
            'risk-pattern-id',
            'Test Risk Pattern',
            logger
        )
        
        success, error_msg = result
        self.assertFalse(success)
        self.assertIsNotNone(error_msg)
        self.assertIn('Bad Request', str(error_msg))
    
    @patch('phase4b_transfer_risk_patterns.requests.post')
    @patch.dict(os.environ, {'API_TOKEN': 'test', 'SUBDOMAIN': 'test'})
    def test_add_risk_pattern_network_error(self, mock_post):
        """Test risk pattern addition with network error"""
        import phase4b_transfer_risk_patterns as phase4b
        
        mock_post.side_effect = requests.exceptions.RequestException("Network Error")
        
        logger = MagicMock()
        
        result = phase4b.add_risk_pattern_to_component(
            'v1-component-id',
            'risk-pattern-id',
            'Test Risk Pattern',
            logger
        )
        
        success, error_msg = result
        self.assertFalse(success)
        self.assertIsNotNone(error_msg)
        self.assertIn('Network Error', str(error_msg))


class TestUtilityFunctions(unittest.TestCase):
    """Unit tests for utility functions across phases"""
    
    def test_json_serialization_special_characters(self):
        """Test JSON handling with special characters"""
        import phase1_collect_v1_components as phase1
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            special_data = [
                {'id': '1', 'name': 'Component with émojis 🚀'},
                {'id': '2', 'name': 'Component with "quotes" and \\backslashes'},
                {'id': '3', 'name': 'Component with\nnewlines\tand\ttabs'}
            ]
            
            result = phase1.save_to_json(special_data, 'special.json')
            
            self.assertTrue(result)
            
            # Verify we can read it back
            with open('special.json', 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.assertEqual(loaded_data, special_data)
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        import phase1_collect_v1_components as phase1
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # Create large dataset
            large_data = []
            for i in range(1000):
                large_data.append({
                    'id': f'comp-{i}',
                    'name': f'Component {i}',
                    'referenceId': f'ref-{i}',
                    'description': 'A' * 100  # Make each item substantial
                })
            
            result = phase1.save_to_json(large_data, 'large.json')
            
            self.assertTrue(result)
            
            # Verify file exists and has reasonable size
            file_size = os.path.getsize('large.json')
            self.assertGreater(file_size, 100000)  # Should be > 100KB


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)