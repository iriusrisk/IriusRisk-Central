#!/usr/bin/env python3
"""
Theme Component Tests

Tests for the Streamlit theme and UI component functionality including:
- CSS loading functionality
- UI component rendering helpers
- IriusRisk branding elements
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestThemeComponents(unittest.TestCase):
    """Test theme.py functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create styles directory and CSS file
        os.makedirs('styles', exist_ok=True)
        with open('styles/iriusrisk.css', 'w') as f:
            f.write("""
/* IriusRisk Theme */
.irius-hero {
    background: linear-gradient(135deg, #00A86B, #2F6FED);
    color: white;
    padding: 2rem;
}

.irius-container {
    max-width: 1200px;
    margin: 0 auto;
}

.irius-h1 {
    font-size: 2.5rem;
    font-weight: 600;
}

.irius-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-outline {
    border: 2px solid #00A86B;
    color: #00A86B;
    padding: 0.5rem 1rem;
    text-decoration: none;
    border-radius: 4px;
}
""")
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    @patch('streamlit.markdown')
    def test_load_css_default_path(self, mock_markdown):
        """Test CSS loading with default path"""
        from theme import load_css
        
        load_css()
        
        # Verify streamlit.markdown was called with CSS content
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        
        # Check that CSS content was wrapped in style tags
        css_content = args[0]
        self.assertIn('<style>', css_content)
        self.assertIn('</style>', css_content)
        self.assertIn('.irius-hero', css_content)
        self.assertIn('background: linear-gradient', css_content)
        
        # Check that unsafe_allow_html was True
        self.assertTrue(kwargs.get('unsafe_allow_html'))
    
    @patch('streamlit.markdown')
    def test_load_css_custom_path(self, mock_markdown):
        """Test CSS loading with custom path"""
        from theme import load_css
        
        # Create custom CSS file
        with open('custom.css', 'w') as f:
            f.write('.custom-class { color: red; }')
        
        load_css('custom.css')
        
        mock_markdown.assert_called_once()
        args, _ = mock_markdown.call_args
        css_content = args[0]
        
        self.assertIn('.custom-class', css_content)
        self.assertIn('color: red', css_content)
    
    @patch('streamlit.markdown')
    def test_load_css_missing_file(self, mock_markdown):
        """Test CSS loading when file doesn't exist"""
        from theme import load_css
        
        # This should raise an exception
        with self.assertRaises(FileNotFoundError):
            load_css('nonexistent.css')
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_hero_component_basic(self, mock_columns, mock_markdown):
        """Test hero component basic functionality"""
        from theme import hero
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = (mock_col1, mock_col2)
        
        title = "Test Title"
        subtitle = "Test subtitle"
        
        hero(title, subtitle)
        
        # Verify markdown calls for structure
        expected_calls = [
            call('<div class="irius-hero irius-container">', unsafe_allow_html=True),
            call("<h1 class='irius-h1' style='margin:0 0 .5rem'>Test Title</h1>", unsafe_allow_html=True),
            call("<p style='margin:0 0 1rem; font-size:1.05rem'>Test subtitle</p>", unsafe_allow_html=True),
            call("</div>", unsafe_allow_html=True)
        ]
        
        for expected_call in expected_calls:
            self.assertIn(expected_call, mock_markdown.call_args_list)
        
        # Verify columns were created
        mock_columns.assert_called_once_with([1,1], gap="large")
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_hero_component_with_callbacks(self, mock_columns, mock_markdown):
        """Test hero component with left and right callbacks"""
        from theme import hero
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = (mock_col1, mock_col2)
        
        # Mock callback functions
        left_callback = MagicMock()
        right_callback = MagicMock()
        
        hero("Title", "Subtitle", left=left_callback, right=right_callback)
        
        # Verify callbacks were called with columns
        left_callback.assert_called_once_with(mock_col1)
        right_callback.assert_called_once_with(mock_col2)
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_hero_component_no_subtitle(self, mock_columns, mock_markdown):
        """Test hero component without subtitle"""
        from theme import hero
        
        # Mock columns
        mock_columns.return_value = (MagicMock(), MagicMock())
        
        hero("Just Title")
        
        # Should not include subtitle paragraph
        subtitle_calls = [call for call in mock_markdown.call_args_list 
                         if 'font-size:1.05rem' in str(call)]
        self.assertEqual(len(subtitle_calls), 0)
    
    @patch('streamlit.markdown')
    def test_card_component(self, mock_markdown):
        """Test card component functionality"""
        from theme import card
        
        title = "Card Title"
        body = "This is the card body content"
        
        card(title, body)
        
        # Verify markdown was called with card HTML
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        
        card_html = args[0]
        self.assertIn('class="irius-card"', card_html)
        self.assertIn('Card Title', card_html)
        self.assertIn('This is the card body content', card_html)
        self.assertIn('class="irius-h3"', card_html)
        self.assertTrue(kwargs.get('unsafe_allow_html'))
    
    @patch('streamlit.markdown')
    def test_card_component_special_characters(self, mock_markdown):
        """Test card component with special characters"""
        from theme import card
        
        title = "Title with <>&\" characters"
        body = "Body with <script>alert('test')</script> content"
        
        card(title, body)
        
        # Verify the content was included (note: real sanitization would be needed in production)
        args, _ = mock_markdown.call_args
        card_html = args[0]
        self.assertIn("Title with <>&\" characters", card_html)
        self.assertIn("Body with <script>alert('test')</script> content", card_html)
    
    @patch('streamlit.markdown')
    def test_outline_button_component(self, mock_markdown):
        """Test outline button component"""
        from theme import outline_button
        
        label = "Click Me"
        href = "https://example.com"
        
        outline_button(label, href)
        
        # Verify markdown was called with button HTML
        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args
        
        button_html = args[0]
        self.assertIn('class="btn-outline"', button_html)
        self.assertIn('href="https://example.com"', button_html)
        self.assertIn('Click Me', button_html)
        self.assertTrue(kwargs.get('unsafe_allow_html'))
    
    @patch('streamlit.markdown')
    def test_outline_button_special_characters(self, mock_markdown):
        """Test outline button with special characters in URL and label"""
        from theme import outline_button
        
        label = "Download & Install"
        href = "https://example.com/path?param=value&other=123"
        
        outline_button(label, href)
        
        args, _ = mock_markdown.call_args
        button_html = args[0]
        self.assertIn('Download & Install', button_html)
        self.assertIn('https://example.com/path?param=value&other=123', button_html)


class TestThemeCSS(unittest.TestCase):
    """Test CSS content and styling"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_css_file_structure(self):
        """Test that CSS file can be read and contains expected elements"""
        
        # Create a basic CSS file to test with
        os.makedirs('styles', exist_ok=True)
        css_content = """
/* IriusRisk Branding */
:root {
    --ir-primary: #00A86B;
    --ir-secondary: #2F6FED;
    --ir-background: #FFFFFF;
}

.irius-hero {
    background: linear-gradient(135deg, var(--ir-primary), var(--ir-secondary));
    color: white;
}

.irius-card {
    background: var(--ir-background);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-outline {
    border: 2px solid var(--ir-primary);
    color: var(--ir-primary);
}
"""
        with open('styles/iriusrisk.css', 'w') as f:
            f.write(css_content)
        
        # Test reading the CSS file
        from pathlib import Path
        css = Path('styles/iriusrisk.css').read_text(encoding="utf-8")
        
        # Verify expected CSS elements
        self.assertIn('--ir-primary: #00A86B', css)
        self.assertIn('--ir-secondary: #2F6FED', css)
        self.assertIn('.irius-hero', css)
        self.assertIn('.irius-card', css)
        self.assertIn('.btn-outline', css)
        self.assertIn('linear-gradient', css)
    
    def test_css_variables_present(self):
        """Test that CSS contains IriusRisk brand variables"""
        
        os.makedirs('styles', exist_ok=True)
        css_content = """
:root {
    --ir-primary: #00A86B;
    --ir-secondary: #2F6FED; 
    --ir-background: #FFFFFF;
    --ir-text: #1F2937;
}
"""
        with open('styles/iriusrisk.css', 'w') as f:
            f.write(css_content)
        
        from pathlib import Path
        css = Path('styles/iriusrisk.css').read_text(encoding="utf-8")
        
        # Check for IriusRisk brand colors
        self.assertIn('#00A86B', css)  # IriusRisk Green
        self.assertIn('#2F6FED', css)  # IriusRisk Blue
        self.assertIn('#FFFFFF', css)  # White background


class TestThemeIntegration(unittest.TestCase):
    """Integration tests for theme components"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create complete styles structure
        os.makedirs('styles', exist_ok=True)
        css_content = """
.irius-hero { background: linear-gradient(135deg, #00A86B, #2F6FED); }
.irius-card { background: white; border-radius: 8px; }
.btn-outline { border: 2px solid #00A86B; }
"""
        with open('styles/iriusrisk.css', 'w') as f:
            f.write(css_content)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    @patch('streamlit.markdown')
    @patch('streamlit.columns')
    def test_complete_page_structure(self, mock_columns, mock_markdown):
        """Test building a complete page with all theme components"""
        from theme import load_css, hero, card, outline_button
        
        mock_columns.return_value = (MagicMock(), MagicMock())
        
        # Simulate building a complete page
        load_css()
        hero("IriusRisk Migration Tool", "Streamline your component migration")
        card("Feature 1", "Real-time migration progress")
        card("Feature 2", "Comprehensive logging")
        outline_button("Get Started", "#start")
        
        # Verify all components were rendered
        markdown_calls = mock_markdown.call_args_list
        
        # Check CSS was loaded
        css_calls = [call for call in markdown_calls if '<style>' in str(call)]
        self.assertGreater(len(css_calls), 0)
        
        # Check hero was rendered
        hero_calls = [call for call in markdown_calls if 'irius-hero' in str(call)]
        self.assertGreater(len(hero_calls), 0)
        
        # Check cards were rendered
        card_calls = [call for call in markdown_calls if 'irius-card' in str(call)]
        self.assertGreaterEqual(len(card_calls), 2)
        
        # Check button was rendered
        button_calls = [call for call in markdown_calls if 'btn-outline' in str(call)]
        self.assertGreater(len(button_calls), 0)


if __name__ == '__main__':
    # Configure test runner for more verbose output
    unittest.main(verbosity=2, buffer=True)