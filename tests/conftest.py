"""Shared pytest fixtures for Bestatic tests"""
import os
import pytest
import yaml
import frontmatter
from pathlib import Path


@pytest.fixture
def minimal_theme(tmp_path):
    """Create a minimal functional theme with basic templates"""
    theme_dir = tmp_path / "themes" / "TestTheme"
    theme_dir.mkdir(parents=True)
    
    # Create templates directory
    templates_dir = theme_dir / "templates"
    templates_dir.mkdir()
    
    # Create basic layout template
    layout_template = """<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
{% block content %}{% endblock %}
</body>
</html>"""
    (templates_dir / "layout.html.jinja2").write_text(layout_template)
    
    # Create post template
    post_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<article>
<h1>{{ post.title }}</h1>
<p>{{ post.date }}</p>
<div>{{ post.content|safe }}</div>
</article>
{% endblock %}"""
    (templates_dir / "post.html.jinja2").write_text(post_template)
    
    # Create page template
    page_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<article>
<h1>{{ page.title }}</h1>
<div>{{ page.content|safe }}</div>
</article>
{% endblock %}"""
    (templates_dir / "page.html.jinja2").write_text(page_template)
    
    # Create list template
    list_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<h1>{{ title }}</h1>
<ul>
{% for post in posts %}
<li><a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
</ul>
{% endblock %}"""
    (templates_dir / "list.html.jinja2").write_text(list_template)
    
    # Create taxonomy template
    taxonomy_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<h1>{{ taxonomy_name }}: {{ taxonomy_item }}</h1>
<ul>
{% for post in posts %}
<li><a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
</ul>
{% endblock %}"""
    (templates_dir / "taxonomy.html.jinja2").write_text(taxonomy_template)
    
    # Create taglist template
    taglist_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<h1>All {{ taxonomy_name }}</h1>
<ul>
{% for item in taxonomy_items %}
<li><a href="{{ item.url }}">{{ item.name }}</a> ({{ item.count }})</li>
{% endfor %}
</ul>
{% endblock %}"""
    (templates_dir / "taglist.html.jinja2").write_text(taglist_template)
    
    # Create home template
    home_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<h1>{{ title }}</h1>
<p>{{ description }}</p>
<ul>
{% for post in posts %}
<li><a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
</ul>
{% endblock %}"""
    (templates_dir / "home.html.jinja2").write_text(home_template)
    
    # Create 404 template
    error_template = """{% extends "layout.html.jinja2" %}
{% block content %}
<h1>404 - Page Not Found</h1>
{% endblock %}"""
    (templates_dir / "404.html.jinja2").write_text(error_template)
    
    # Create static directory
    static_dir = theme_dir / "static" / "css"
    static_dir.mkdir(parents=True)
    (static_dir / "style.css").write_text("body { margin: 0; }")
    
    return theme_dir


@pytest.fixture
def sample_config(tmp_path):
    """Return a minimal valid configuration dictionary"""
    return {
        "siteURL": "http://example.org",
        "title": "Test Site",
        "description": "A test website",
        "theme": "TestTheme",
        "time_format": "%B %d, %Y",
        "number_of_pages": 1,
        "markdown": {
            "extensions": ["codehilite", "fenced_code", "tables"],
            "extension_configs": {
                "codehilite": {"css_class": "highlight"}
            }
        },
        "taxonomies": {
            "tags": {
                "url": "/tags",
                "taxonomy_template": "taxonomy.html.jinja2",
                "taxonomy_directory": "tags"
            }
        }
    }


@pytest.fixture
def sample_posts(tmp_path):
    """Create sample markdown posts with frontmatter"""
    posts_dir = tmp_path / "posts"
    posts_dir.mkdir()
    
    # Post 1
    post1_dict = {
        'title': 'First Post',
        'date': 'January 01, 2024',
        'tags': 'python, testing',
        'description': 'The first test post',
        'slug': 'first-post'
    }
    post1_content = "This is the first post. It has **markdown** content."
    post1 = frontmatter.Post(post1_content, **post1_dict)
    (posts_dir / "first-post.md").write_text(frontmatter.dumps(post1))
    
    # Post 2
    post2_dict = {
        'title': 'Second Post',
        'date': 'January 15, 2024',
        'tags': ['python', 'bestatic'],
        'description': 'The second test post',
        'slug': 'second-post'
    }
    post2_content = "This is the second post with a [link](https://example.com)."
    post2 = frontmatter.Post(post2_content, **post2_dict)
    (posts_dir / "second-post.md").write_text(frontmatter.dumps(post2))
    
    return posts_dir


@pytest.fixture
def sample_pages(tmp_path):
    """Create sample markdown pages"""
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    
    # About page
    about_dict = {
        'title': 'About',
        'description': 'About this site',
        'slug': 'about'
    }
    about_content = "This is the about page."
    about = frontmatter.Post(about_content, **about_dict)
    (pages_dir / "about.md").write_text(frontmatter.dumps(about))
    
    # Contact page
    contact_dict = {
        'title': 'Contact',
        'description': 'Contact information',
        'slug': 'contact'
    }
    contact_content = "Contact us at test@example.com"
    contact = frontmatter.Post(contact_content, **contact_dict)
    (pages_dir / "contact.md").write_text(frontmatter.dumps(contact))
    
    return pages_dir


@pytest.fixture
def data_files(tmp_path):
    """Create CSV and YAML data files"""
    datafiles_dir = tmp_path / "_includes" / "datafiles"
    datafiles_dir.mkdir(parents=True)
    
    # CSV file
    csv_content = """name,role,email
Alice,Developer,alice@example.com
Bob,Designer,bob@example.com
Charlie,Manager,charlie@example.com"""
    (datafiles_dir / "team.csv").write_text(csv_content)
    
    # YAML file
    yaml_content = {
        'site_info': {
            'name': 'Test Site',
            'version': '1.0',
            'features': ['posts', 'pages', 'taxonomies']
        },
        'social': {
            'twitter': '@testsite',
            'github': 'testuser'
        }
    }
    with open(datafiles_dir / "config.yaml", 'w') as f:
        yaml.dump(yaml_content, f)
    
    return datafiles_dir


@pytest.fixture
def mock_shortcodes(tmp_path):
    """Create mock shortcode modules"""
    shortcodes_dir = tmp_path / "_shortcodes"
    shortcodes_dir.mkdir()
    
    # Alert shortcode
    alert_code = """def render(attrs):
    alert_type = attrs.get('type', 'info')
    content = attrs.get('content', '')
    return f'<div class="alert alert-{alert_type}">{content}</div>'
"""
    (shortcodes_dir / "alert.py").write_text(alert_code)
    
    # Test shortcode
    test_code = """def render(attrs):
    return '<div class="test">Test shortcode</div>'
"""
    (shortcodes_dir / "test.py").write_text(test_code)
    
    return shortcodes_dir


@pytest.fixture
def test_site(tmp_path, minimal_theme, sample_posts, sample_pages, sample_config, data_files):
    """Complete test site structure with all components"""
    # Change to the test directory
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    # Write config file
    with open(tmp_path / "bestatic.yaml", 'w') as f:
        yaml.dump(sample_config, f)
    
    # Create _output directory
    output_dir = tmp_path / "_output"
    output_dir.mkdir()
    
    yield tmp_path
    
    # Cleanup: restore original directory
    os.chdir(original_cwd)


@pytest.fixture
def test_site_with_shortcodes(tmp_path, minimal_theme, sample_posts, sample_pages, 
                                sample_config, data_files, mock_shortcodes):
    """Complete test site with shortcodes enabled"""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    # Update config to enable shortcodes
    config = sample_config.copy()
    config['enable_shortcodes'] = True
    
    # Write config file
    with open(tmp_path / "bestatic.yaml", 'w') as f:
        yaml.dump(config, f)
    
    # Create _output directory
    output_dir = tmp_path / "_output"
    output_dir.mkdir()
    
    yield tmp_path
    
    os.chdir(original_cwd)
