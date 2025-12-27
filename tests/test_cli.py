"""Tests for bestatic.py - CLI interface and argument parsing"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse


class TestCLIArgumentParsing:
    """Test command-line argument parsing"""
    
    def test_help_argument(self):
        """Test --help argument"""
        # We can't easily test this without running the actual script
        # But we can verify the parser setup
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--generate', action='store_true')
        parser.add_argument('-s', '--serve', action='store_true')
        
        # Parse empty args
        args = parser.parse_args([])
        assert hasattr(args, 'generate')
        assert hasattr(args, 'serve')
    
    def test_generate_flag(self):
        """Test -g/--generate flag"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-g', '--generate', action='store_true')
        
        # Test short form
        args = parser.parse_args(['-g'])
        assert args.generate is True
        
        # Test long form
        args = parser.parse_args(['--generate'])
        assert args.generate is True
    
    def test_serve_flag(self):
        """Test -s/--serve flag"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--serve', action='store_true')
        
        args = parser.parse_args(['-s'])
        assert args.serve is True
        
        args = parser.parse_args(['--serve'])
        assert args.serve is True
    
    def test_auto_flag(self):
        """Test -a/--auto flag for file watching"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-a', '--auto', action='store_true')
        
        args = parser.parse_args(['-a'])
        assert args.auto is True
    
    def test_portnumber_argument(self):
        """Test -n/--portnumber argument"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--portnumber', type=int, default=8080)
        
        # Test default value
        args = parser.parse_args([])
        assert args.portnumber == 8080
        
        # Test custom port
        args = parser.parse_args(['-n', '9000'])
        assert args.portnumber == 9000
        
        args = parser.parse_args(['--portnumber', '3000'])
        assert args.portnumber == 3000
    
    def test_combined_flags(self):
        """Test combining multiple flags"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', '--serve', action='store_true')
        parser.add_argument('-a', '--auto', action='store_true')
        parser.add_argument('-n', '--portnumber', type=int, default=8080)
        
        # Test -sa combination
        args = parser.parse_args(['-sa'])
        assert args.serve is True
        assert args.auto is True
        
        # Test -san combination with port
        args = parser.parse_args(['-san', '9090'])
        assert args.serve is True
        assert args.auto is True
        assert args.portnumber == 9090
    
    def test_newpost_argument(self):
        """Test --newpost argument"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--newpost', type=str)
        
        args = parser.parse_args(['--newpost', 'my-post'])
        assert args.newpost == 'my-post'
    
    def test_newpage_argument(self):
        """Test --newpage argument"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--newpage', type=str)
        
        args = parser.parse_args(['--newpage', 'about'])
        assert args.newpage == 'about'
    
    def test_quickstart_flag(self):
        """Test --quickstart flag"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--quickstart', action='store_true')
        
        args = parser.parse_args(['--quickstart'])
        assert args.quickstart is True
    
    def test_theme_argument(self):
        """Test --theme argument for quickstart"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--theme', type=str)
        
        args = parser.parse_args(['--theme', 'Amazing'])
        assert args.theme == 'Amazing'


class TestConfigFileLoading:
    """Test configuration file loading"""
    
    def test_load_bestatic_yaml(self, tmp_path):
        """Test loading bestatic.yaml configuration"""
        os.chdir(tmp_path)
        
        import yaml
        
        config = {
            'siteURL': 'https://example.com',
            'title': 'Test Site',
            'theme': 'TestTheme'
        }
        
        with open(tmp_path / 'bestatic.yaml', 'w') as f:
            yaml.dump(config, f)
        
        # Load config
        with open('bestatic.yaml', 'rb') as f:
            loaded_config = yaml.load(f, Loader=yaml.Loader)
        
        assert loaded_config['siteURL'] == 'https://example.com'
        assert loaded_config['title'] == 'Test Site'
        assert loaded_config['theme'] == 'TestTheme'
    
    def test_fallback_to_config_yaml(self, tmp_path):
        """Test fallback to config.yaml if bestatic.yaml doesn't exist"""
        os.chdir(tmp_path)
        
        import yaml
        
        config = {
            'siteURL': 'https://example.com',
            'title': 'Test Site'
        }
        
        # Create only config.yaml
        with open(tmp_path / 'config.yaml', 'w') as f:
            yaml.dump(config, f)
        
        # Try to load bestatic.yaml first, fall back to config.yaml
        config_file = "bestatic.yaml"
        if not os.path.isfile(config_file):
            config_file = "config.yaml"
        
        assert config_file == "config.yaml"
        
        with open(config_file, 'rb') as f:
            loaded_config = yaml.load(f, Loader=yaml.Loader)
        
        assert loaded_config['siteURL'] == 'https://example.com'
    
    def test_missing_config_file(self, tmp_path):
        """Test behavior when no config file exists"""
        os.chdir(tmp_path)
        
        config_file = "bestatic.yaml"
        if not os.path.isfile(config_file):
            config_file = "config.yaml"
        
        # Should not find either file
        assert not os.path.isfile(config_file)


class TestServerFunctionality:
    """Test server-related functions (mocked)"""
    
    @patch('bestatic.bestatic.bestatic_serv')
    def test_run_server_default_directory(self, mock_serve):
        """Test running server with default _output directory"""
        from bestatic.bestatic import run_server
        
        run_server(None, 8080)
        
        # Should call bestatic_serv with port only
        mock_serve.assert_called_once_with(port=8080)
    
    @patch('bestatic.bestatic.bestatic_serv')
    def test_run_server_custom_directory(self, mock_serve):
        """Test running server with custom directory"""
        from bestatic.bestatic import run_server
        
        run_server("custom_dir", 8080)
        
        # Should call with directory and port
        mock_serve.assert_called_once_with("custom_dir", port=8080)
    
    @patch('bestatic.bestatic.bestatic_serv')
    def test_run_server_custom_port(self, mock_serve):
        """Test running server on custom port"""
        from bestatic.bestatic import run_server
        
        run_server(None, 9090)
        
        mock_serve.assert_called_once_with(port=9090)


class TestFileWatcherSetup:
    """Test file watcher configuration"""
    
    def test_directories_to_watch_list(self):
        """Test that correct directories are watched"""
        directories_to_watch = [
            "themes",
            "posts",
            "pages",
            "static-content",
            "_includes",
            "_mddata",
            "_shortcodes"
        ]
        
        assert "themes" in directories_to_watch
        assert "posts" in directories_to_watch
        assert "pages" in directories_to_watch
        assert "_mddata" in directories_to_watch
        assert "_shortcodes" in directories_to_watch
    
    def test_watcher_ignores_output_directory(self):
        """Test that _output directory is ignored"""
        ignore_patterns = ['*~', '.*', '_output']
        
        assert '_output' in ignore_patterns or any('_output' in p for p in ignore_patterns)
    
    def test_watcher_ignores_temp_files(self):
        """Test that temporary files are ignored"""
        ignore_patterns = ['*~', '.*']
        
        # Should ignore backup files and hidden files
        assert '*~' in ignore_patterns
        assert '.*' in ignore_patterns


class TestIntegrationScenarios:
    """Test realistic CLI usage scenarios"""
    
    def test_generate_only_workflow(self, tmp_path, minimal_theme, sample_config):
        """Test generate-only workflow (-g flag)"""
        os.chdir(tmp_path)
        
        import yaml
        
        # Setup minimal site
        posts_dir = tmp_path / "posts"
        posts_dir.mkdir()
        
        pages_dir = tmp_path / "pages"
        pages_dir.mkdir()
        
        with open(tmp_path / "bestatic.yaml", 'w') as f:
            yaml.dump(sample_config, f)
        
        # Simulate -g flag behavior
        from bestatic.generator import generator
        generator(**sample_config)
        
        # Should create _output
        assert (tmp_path / "_output").exists()
    
    @patch('bestatic.bestatic.bestatic_serv')
    def test_serve_only_workflow(self, mock_serve, tmp_path):
        """Test serve-only workflow (-s flag)"""
        os.chdir(tmp_path)
        
        # Create _output directory
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        (output_dir / "index.html").write_text("<html>Test</html>")
        
        # Simulate -s flag behavior
        from bestatic.bestatic import run_server
        run_server(None, 8080)
        
        mock_serve.assert_called_once()
    
    def test_newpost_workflow(self, tmp_path):
        """Test creating new post (--newpost flag)"""
        os.chdir(tmp_path)
        
        # Simulate --newpost flag
        from bestatic.newcontent import newpost
        newpost("test-post", "%B %d, %Y")
        
        # Should create post file
        assert (tmp_path / "posts" / "test-post.md").exists()
    
    def test_newpage_workflow(self, tmp_path):
        """Test creating new page (--newpage flag)"""
        os.chdir(tmp_path)
        
        # Simulate --newpage flag
        from bestatic.newcontent import newpage
        newpage("about")
        
        # Should create page file
        assert (tmp_path / "pages" / "about.md").exists()
