"""Tests for quickstart.py - Interactive project setup"""
import os
import pytest
import yaml
import frontmatter
from pathlib import Path
from unittest.mock import patch, MagicMock
from bestatic.quickstart import quickstart


class TestQuickstartBasic:
    """Test basic quickstart functionality"""
    
    @patch('builtins.input', side_effect=['My Test Site', 'A test website for Bestatic'])
    def test_quickstart_creates_config(self, mock_input, tmp_path, minimal_theme):
        """Test that quickstart creates bestatic.yaml"""
        os.chdir(tmp_path)
        
        # Run quickstart
        config = quickstart(theme="TestTheme")
        
        # Check config file exists
        config_file = tmp_path / "bestatic.yaml"
        assert config_file.exists()
        
        # Load and verify config
        with open(config_file, 'r') as f:
            loaded_config = yaml.safe_load(f)
        
        assert loaded_config['title'] == 'My Test Site'
        assert loaded_config['description'] == 'A test website for Bestatic'
        assert loaded_config['theme'] == 'TestTheme'
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_creates_posts(self, mock_input, tmp_path, minimal_theme):
        """Test that quickstart creates sample posts"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Check posts directory exists
        posts_dir = tmp_path / "posts"
        assert posts_dir.exists()
        
        # Check for sample posts
        post_files = list(posts_dir.glob("*.md"))
        assert len(post_files) == 2
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_creates_pages(self, mock_input, tmp_path, minimal_theme):
        """Test that quickstart creates sample pages"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Check pages directory exists
        pages_dir = tmp_path / "pages"
        assert pages_dir.exists()
        
        # Check for sample pages
        page_files = list(pages_dir.glob("*.md"))
        assert len(page_files) == 2
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_default_theme(self, mock_input, tmp_path):
        """Test that quickstart uses Amazing theme by default"""
        os.chdir(tmp_path)
        
        # Create Amazing theme directory
        theme_dir = tmp_path / "themes" / "Amazing"
        theme_dir.mkdir(parents=True)
        
        config = quickstart()
        
        assert config['theme'] == 'Amazing'
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_custom_theme(self, mock_input, tmp_path, minimal_theme):
        """Test quickstart with custom theme"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        assert config['theme'] == 'TestTheme'


class TestQuickstartConfiguration:
    """Test configuration generation"""
    
    @patch('builtins.input', side_effect=['My Blog', 'Personal blog'])
    def test_config_default_values(self, mock_input, tmp_path, minimal_theme):
        """Test that config has correct default values"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        assert config['siteURL'] == 'http://example.org'
        assert config['time_format'] == '%B %d, %Y'
        assert config['number_of_pages'] == 1
    
    @patch('builtins.input', side_effect=['Test', 'Description'])
    def test_config_user_input(self, mock_input, tmp_path, minimal_theme):
        """Test that user input is captured in config"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        assert config['title'] == 'Test'
        assert config['description'] == 'Description'
    
    @patch('builtins.input', side_effect=['', 'Valid Title', '', 'Valid Description'])
    def test_empty_input_validation(self, mock_input, tmp_path, minimal_theme):
        """Test that empty inputs are rejected"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        # Should have valid values after retries
        assert config['title'] != ''
        assert config['description'] != ''


class TestQuickstartContent:
    """Test sample content generation"""
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_sample_post_structure(self, mock_input, tmp_path, minimal_theme):
        """Test that sample posts have correct structure"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Load a sample post
        post_files = list((tmp_path / "posts").glob("*.md"))
        assert len(post_files) > 0
        
        with open(post_files[0], 'r') as f:
            post = frontmatter.load(f)
        
        # Check required fields
        assert 'title' in post.metadata
        assert 'date' in post.metadata
        assert 'tags' in post.metadata
        assert 'description' in post.metadata
        assert 'slug' in post.metadata
        assert len(post.content) > 0
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_sample_post_slugs(self, mock_input, tmp_path, minimal_theme):
        """Test that sample posts have different slugs"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        posts_dir = tmp_path / "posts"
        post_files = list(posts_dir.glob("*.md"))
        
        slugs = []
        for post_file in post_files:
            with open(post_file, 'r') as f:
                post = frontmatter.load(f)
                slugs.append(post.metadata['slug'])
        
        # All slugs should be unique
        assert len(slugs) == len(set(slugs))
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_sample_page_structure(self, mock_input, tmp_path, minimal_theme):
        """Test that sample pages have correct structure"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Load a sample page
        page_files = list((tmp_path / "pages").glob("*.md"))
        assert len(page_files) > 0
        
        with open(page_files[0], 'r') as f:
            page = frontmatter.load(f)
        
        # Check required fields
        assert 'title' in page.metadata
        assert 'description' in page.metadata
        assert 'slug' in page.metadata
        assert 'date' not in page.metadata  # Pages don't have dates
        assert len(page.content) > 0
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_about_page_created(self, mock_input, tmp_path, minimal_theme):
        """Test that About page is created"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Check for about.md
        about_file = tmp_path / "pages" / "about.md"
        assert about_file.exists()
        
        with open(about_file, 'r') as f:
            page = frontmatter.load(f)
        
        assert page.metadata['slug'] == 'about'
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_contact_page_created(self, mock_input, tmp_path, minimal_theme):
        """Test that Contact page is created"""
        os.chdir(tmp_path)
        
        quickstart(theme="TestTheme")
        
        # Check for contact.md
        contact_file = tmp_path / "pages" / "contact.md"
        assert contact_file.exists()
        
        with open(contact_file, 'r') as f:
            page = frontmatter.load(f)
        
        assert page.metadata['slug'] == 'contact'


class TestQuickstartErrorHandling:
    """Test error handling in quickstart"""
    
    def test_missing_theme_directory(self, tmp_path):
        """Test error when theme directory doesn't exist"""
        os.chdir(tmp_path)
        
        # Try to use non-existent theme
        with pytest.raises(FileNotFoundError):
            quickstart(theme="NonExistentTheme")
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_creates_directories(self, mock_input, tmp_path, minimal_theme):
        """Test that necessary directories are created"""
        os.chdir(tmp_path)
        
        # Ensure directories don't exist
        if (tmp_path / "posts").exists():
            import shutil
            shutil.rmtree(tmp_path / "posts")
        if (tmp_path / "pages").exists():
            import shutil
            shutil.rmtree(tmp_path / "pages")
        
        quickstart(theme="TestTheme")
        
        # Directories should now exist
        assert (tmp_path / "posts").exists()
        assert (tmp_path / "pages").exists()


class TestQuickstartReturnValue:
    """Test quickstart return value"""
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_quickstart_returns_config(self, mock_input, tmp_path, minimal_theme):
        """Test that quickstart returns configuration dictionary"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        assert isinstance(config, dict)
        assert 'siteURL' in config
        assert 'title' in config
        assert 'description' in config
        assert 'theme' in config
    
    @patch('builtins.input', side_effect=['Test Site', 'Test Description'])
    def test_returned_config_matches_file(self, mock_input, tmp_path, minimal_theme):
        """Test that returned config matches saved file"""
        os.chdir(tmp_path)
        
        returned_config = quickstart(theme="TestTheme")
        
        # Load config from file
        with open(tmp_path / "bestatic.yaml", 'r') as f:
            file_config = yaml.safe_load(f)
        
        assert returned_config['title'] == file_config['title']
        assert returned_config['description'] == file_config['description']
        assert returned_config['theme'] == file_config['theme']


class TestQuickstartIntegration:
    """Integration tests for quickstart workflow"""
    
    @patch('builtins.input', side_effect=['My Blog', 'A personal blog'])
    def test_full_quickstart_workflow(self, mock_input, tmp_path, minimal_theme):
        """Test complete quickstart workflow"""
        os.chdir(tmp_path)
        
        # Run quickstart
        config = quickstart(theme="TestTheme")
        
        # Verify all components exist
        assert (tmp_path / "bestatic.yaml").exists()
        assert (tmp_path / "posts").exists()
        assert (tmp_path / "pages").exists()
        
        # Verify content was created
        assert len(list((tmp_path / "posts").glob("*.md"))) == 2
        assert len(list((tmp_path / "pages").glob("*.md"))) == 2
        
        # Verify config is valid
        assert config['title'] == 'My Blog'
        assert config['description'] == 'A personal blog'
    
    @patch('builtins.input', side_effect=['Test', 'Description'])
    def test_quickstart_ready_for_generation(self, mock_input, tmp_path, minimal_theme):
        """Test that site is ready for generation after quickstart"""
        os.chdir(tmp_path)
        
        config = quickstart(theme="TestTheme")
        
        # Should be able to run generator
        from bestatic.generator import generator
        generator(**config)
        
        # Check output was created
        assert (tmp_path / "_output").exists()
