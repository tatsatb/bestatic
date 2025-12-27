"""Tests for newcontent.py - Post and page creation utilities"""
import os
import pytest
import frontmatter
from pathlib import Path
from bestatic.newcontent import newpost, newpage


class TestNewPost:
    """Test post creation functionality"""
    
    def test_create_simple_post(self, tmp_path):
        """Test creating a basic post"""
        os.chdir(tmp_path)
        
        # Create post
        filepath = "test-post"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        # Check file was created
        post_file = tmp_path / "posts" / f"{filepath}.md"
        assert post_file.exists()
        
        # Load and verify frontmatter
        with open(post_file, 'r') as f:
            post = frontmatter.load(f)
        
        assert post.metadata['title'] == "This is a sample post"
        assert post.metadata['slug'] == filepath
        assert 'date' in post.metadata
        assert 'tags' in post.metadata
        assert 'description' in post.metadata
    
    def test_create_post_with_subdirectory(self, tmp_path):
        """Test creating post in subdirectory"""
        os.chdir(tmp_path)
        
        # Create post with path
        filepath = "2024/01/my-post"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        # Check file and directory structure
        post_file = tmp_path / "posts" / f"{filepath}.md"
        assert post_file.exists()
        
        # Verify parent directories were created
        assert (tmp_path / "posts" / "2024" / "01").is_dir()
    
    def test_post_content_is_markdown(self, tmp_path):
        """Test that post content is written correctly"""
        os.chdir(tmp_path)
        
        filepath = "content-test"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        post_file = tmp_path / "posts" / f"{filepath}.md"
        
        with open(post_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Check content exists
        assert len(post.content) > 0
        assert "example post content" in post.content
    
    def test_post_tags_format(self, tmp_path):
        """Test that tags are formatted correctly"""
        os.chdir(tmp_path)
        
        filepath = "tags-test"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        post_file = tmp_path / "posts" / f"{filepath}.md"
        
        with open(post_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Tags should be a string
        assert isinstance(post.metadata['tags'], str)
        assert 'sample-tag-1' in post.metadata['tags']
        assert 'sample-tag-2' in post.metadata['tags']
    
    def test_post_date_format(self, tmp_path):
        """Test that date is formatted according to time_format"""
        os.chdir(tmp_path)
        
        filepath = "date-test"
        time_format = "%Y-%m-%d"
        newpost(filepath, time_format)
        
        post_file = tmp_path / "posts" / f"{filepath}.md"
        
        with open(post_file, 'r') as f:
            post = frontmatter.load(f)
        
        # Date should be in YYYY-MM-DD format
        date_str = post.metadata['date']
        assert len(date_str.split('-')) == 3
    
    def test_posts_directory_creation(self, tmp_path):
        """Test that posts directory is created if it doesn't exist"""
        os.chdir(tmp_path)
        
        # Ensure posts directory doesn't exist
        posts_dir = tmp_path / "posts"
        if posts_dir.exists():
            import shutil
            shutil.rmtree(posts_dir)
        
        filepath = "new-post"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        # Directory should now exist
        assert posts_dir.exists()
        assert posts_dir.is_dir()


class TestNewPage:
    """Test page creation functionality"""
    
    def test_create_simple_page(self, tmp_path):
        """Test creating a basic page"""
        os.chdir(tmp_path)
        
        # Create page
        filepath = "about"
        newpage(filepath)
        
        # Check file was created
        page_file = tmp_path / "pages" / f"{filepath}.md"
        assert page_file.exists()
        
        # Load and verify frontmatter
        with open(page_file, 'r') as f:
            page = frontmatter.load(f)
        
        assert page.metadata['title'] == "This is a sample page"
        assert page.metadata['slug'] == filepath
        assert 'description' in page.metadata
        assert 'date' not in page.metadata  # Pages don't have dates
    
    def test_create_page_with_subdirectory(self, tmp_path):
        """Test creating page in subdirectory"""
        os.chdir(tmp_path)
        
        # Create page with path
        filepath = "docs/getting-started"
        newpage(filepath)
        
        # Check file and directory structure
        page_file = tmp_path / "pages" / f"{filepath}.md"
        assert page_file.exists()
        
        # Verify parent directories were created
        assert (tmp_path / "pages" / "docs").is_dir()
    
    def test_page_content_is_markdown(self, tmp_path):
        """Test that page content is written correctly"""
        os.chdir(tmp_path)
        
        filepath = "content-test"
        newpage(filepath)
        
        page_file = tmp_path / "pages" / f"{filepath}.md"
        
        with open(page_file, 'r') as f:
            page = frontmatter.load(f)
        
        # Check content exists
        assert len(page.content) > 0
        assert "example page content" in page.content
    
    def test_page_no_tags(self, tmp_path):
        """Test that pages don't have tags"""
        os.chdir(tmp_path)
        
        filepath = "no-tags"
        newpage(filepath)
        
        page_file = tmp_path / "pages" / f"{filepath}.md"
        
        with open(page_file, 'r') as f:
            page = frontmatter.load(f)
        
        # Pages should not have tags
        assert 'tags' not in page.metadata
    
    def test_pages_directory_creation(self, tmp_path):
        """Test that pages directory is created if it doesn't exist"""
        os.chdir(tmp_path)
        
        # Ensure pages directory doesn't exist
        pages_dir = tmp_path / "pages"
        if pages_dir.exists():
            import shutil
            shutil.rmtree(pages_dir)
        
        filepath = "new-page"
        newpage(filepath)
        
        # Directory should now exist
        assert pages_dir.exists()
        assert pages_dir.is_dir()
    
    def test_page_slug_matches_filename(self, tmp_path):
        """Test that page slug matches the provided filename"""
        os.chdir(tmp_path)
        
        filepath = "contact-us"
        newpage(filepath)
        
        page_file = tmp_path / "pages" / f"{filepath}.md"
        
        with open(page_file, 'r') as f:
            page = frontmatter.load(f)
        
        assert page.metadata['slug'] == filepath


class TestContentCreationEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_multiple_posts(self, tmp_path):
        """Test creating multiple posts"""
        os.chdir(tmp_path)
        
        time_format = "%B %d, %Y"
        
        # Create multiple posts
        newpost("post1", time_format)
        newpost("post2", time_format)
        newpost("post3", time_format)
        
        posts_dir = tmp_path / "posts"
        
        # All should exist
        assert (posts_dir / "post1.md").exists()
        assert (posts_dir / "post2.md").exists()
        assert (posts_dir / "post3.md").exists()
    
    def test_create_multiple_pages(self, tmp_path):
        """Test creating multiple pages"""
        os.chdir(tmp_path)
        
        # Create multiple pages
        newpage("page1")
        newpage("page2")
        newpage("page3")
        
        pages_dir = tmp_path / "pages"
        
        # All should exist
        assert (pages_dir / "page1.md").exists()
        assert (pages_dir / "page2.md").exists()
        assert (pages_dir / "page3.md").exists()
    
    def test_filename_with_special_characters(self, tmp_path):
        """Test creating post/page with special characters in name"""
        os.chdir(tmp_path)
        
        # Most special characters in filenames should work
        filepath = "my-post_2024"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        post_file = tmp_path / "posts" / f"{filepath}.md"
        assert post_file.exists()
    
    def test_deeply_nested_path(self, tmp_path):
        """Test creating content in deeply nested directory"""
        os.chdir(tmp_path)
        
        filepath = "year/month/day/category/post-name"
        time_format = "%B %d, %Y"
        newpost(filepath, time_format)
        
        post_file = tmp_path / "posts" / f"{filepath}.md"
        assert post_file.exists()
        
        # Verify all parent directories exist
        assert post_file.parent.exists()
