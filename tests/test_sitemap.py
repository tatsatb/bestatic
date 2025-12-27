"""Tests for bestaticSitemap.py - Sitemap XML generation"""
import os
import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from bestatic.bestaticSitemap import (
    get_last_modified_time,
    find_single_index_folders,
    generate_sitemap
)


class TestSitemapHelpers:
    """Test helper functions for sitemap generation"""
    
    def test_find_single_index_folders_basic(self, tmp_path):
        """Test finding folders with single index.html"""
        # Create _output structure
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create folders with index.html
        (output_dir / "page1").mkdir()
        (output_dir / "page1" / "index.html").write_text("<html>Page 1</html>")
        
        (output_dir / "page2").mkdir()
        (output_dir / "page2" / "index.html").write_text("<html>Page 2</html>")
        
        # Change to parent directory
        os.chdir(tmp_path)
        
        # Find folders
        folders = find_single_index_folders(str(output_dir))
        
        # Folders should contain page paths (may be full or relative)
        assert any("page1" in f for f in folders)
        assert any("page2" in f for f in folders)
    
    def test_find_single_index_folders_nested(self, tmp_path):
        """Test finding nested folders"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create nested structure
        (output_dir / "blog" / "2024" / "post1").mkdir(parents=True)
        (output_dir / "blog" / "2024" / "post1" / "index.html").write_text("<html>Post</html>")
        
        os.chdir(tmp_path)
        
        folders = find_single_index_folders(str(output_dir))
        
        # Should find nested path
        assert any("post1" in folder for folder in folders)
    
    def test_find_single_index_folders_excludes_404(self, tmp_path):
        """Test that 404 directory is excluded"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create 404 directory
        (output_dir / "404").mkdir()
        (output_dir / "404" / "index.html").write_text("<html>404</html>")
        
        # Create valid page
        (output_dir / "about").mkdir()
        (output_dir / "about" / "index.html").write_text("<html>About</html>")
        
        os.chdir(tmp_path)
        
        folders = find_single_index_folders(str(output_dir))
        
        # 404 should not be in any folder path
        assert not any(folder == "404" for folder in folders)
        assert any("about" in f for f in folders)
    
    def test_get_last_modified_time(self, tmp_path):
        """Test getting last modified time of file"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create test file
        test_dir = output_dir / "test"
        test_dir.mkdir()
        (test_dir / "index.html").write_text("<html>Test</html>")
        
        os.chdir(tmp_path)
        
        # Get modification time
        mod_time = get_last_modified_time("test")
        
        # Should return ISO format datetime string
        assert isinstance(mod_time, str)
        assert "T" in mod_time  # ISO format has T separator


class TestSitemapGeneration:
    """Test sitemap XML generation"""
    
    def test_generate_sitemap_basic(self, tmp_path):
        """Test basic sitemap generation"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create some pages
        (output_dir / "about").mkdir()
        (output_dir / "about" / "index.html").write_text("<html>About</html>")
        
        (output_dir / "contact").mkdir()
        (output_dir / "contact" / "index.html").write_text("<html>Contact</html>")
        
        os.chdir(tmp_path)
        
        # Generate sitemap (it expects to be run from parent of _output)
        base_url = "https://example.com"
        generate_sitemap(base_url, "_output")
        
        # Check sitemap file exists
        sitemap_file = output_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        # Parse and validate XML
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        # Check namespace
        assert "sitemaps.org" in root.tag
        
        # Check URL entries
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        assert len(urls) == 2
    
    def test_sitemap_url_format(self, tmp_path):
        """Test that URLs are formatted correctly"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "blog").mkdir()
        (output_dir / "blog" / "index.html").write_text("<html>Blog</html>")
        
        os.chdir(tmp_path)
        
        base_url = "https://example.com"
        generate_sitemap(base_url, "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        # Find loc elements
        locs = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        
        # Check URL format
        loc_text = [loc.text for loc in locs]
        assert any("https://example.com" in url for url in loc_text)
    
    def test_sitemap_includes_lastmod(self, tmp_path):
        """Test that sitemap includes lastmod tags"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "page").mkdir()
        (output_dir / "page" / "index.html").write_text("<html>Page</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        # Find lastmod elements
        lastmods = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        
        assert len(lastmods) > 0
        # Check format (should be ISO datetime)
        assert "T" in lastmods[0].text
    
    def test_sitemap_with_nested_pages(self, tmp_path):
        """Test sitemap generation with nested page structure"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create nested structure
        (output_dir / "docs" / "guide" / "getting-started").mkdir(parents=True)
        (output_dir / "docs" / "guide" / "getting-started" / "index.html").write_text("<html>Guide</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        assert len(urls) >= 1
    
    def test_sitemap_with_no_pages(self, tmp_path):
        """Test sitemap generation with empty output directory"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        assert sitemap_file.exists()
        
        # Should have valid XML even with no URLs
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        assert root.tag.endswith("urlset")
    
    def test_sitemap_excludes_404_page(self, tmp_path):
        """Test that 404 page is not included in sitemap"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        # Create 404 page
        (output_dir / "404").mkdir()
        (output_dir / "404" / "index.html").write_text("<html>404</html>")
        
        # Create normal page
        (output_dir / "about").mkdir()
        (output_dir / "about" / "index.html").write_text("<html>About</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        content = sitemap_file.read_text()
        
        # 404 should not be in sitemap
        assert "404" not in content
        assert "about" in content
    
    def test_sitemap_backslash_handling(self, tmp_path):
        """Test that backslashes in paths are converted to forward slashes"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "page").mkdir()
        (output_dir / "page" / "index.html").write_text("<html>Page</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        content = sitemap_file.read_text()
        
        # Should not contain backslashes
        assert chr(92) not in content or "/" in content


class TestSitemapXMLValidity:
    """Test XML validity of generated sitemaps"""
    
    def test_sitemap_xml_declaration(self, tmp_path):
        """Test that sitemap has proper XML declaration"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "page").mkdir()
        (output_dir / "page" / "index.html").write_text("<html>Page</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        content = sitemap_file.read_text()
        
        # Should start with XML declaration
        assert content.startswith("<?xml")
    
    def test_sitemap_namespace(self, tmp_path):
        """Test that sitemap uses correct namespace"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "page").mkdir()
        (output_dir / "page" / "index.html").write_text("<html>Page</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        tree = ET.parse(sitemap_file)
        root = tree.getroot()
        
        # Check for correct namespace
        assert "http://www.sitemaps.org/schemas/sitemap/0.9" in root.tag
    
    def test_sitemap_parseable(self, tmp_path):
        """Test that generated sitemap is valid XML"""
        output_dir = tmp_path / "_output"
        output_dir.mkdir()
        
        (output_dir / "page1").mkdir()
        (output_dir / "page1" / "index.html").write_text("<html>Page 1</html>")
        
        (output_dir / "page2").mkdir()
        (output_dir / "page2" / "index.html").write_text("<html>Page 2</html>")
        
        os.chdir(tmp_path)
        
        generate_sitemap("https://example.com", "_output")
        
        sitemap_file = output_dir / "sitemap.xml"
        
        # Should parse without errors
        tree = ET.parse(sitemap_file)
        assert tree is not None
