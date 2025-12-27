from setuptools import setup, find_packages
import subprocess
import os


def get_version():
    """Get version from git tag, version file, or fall back to default."""
    version_file = os.path.join(
        os.path.dirname(__file__), "bestatic", "_version.py"
    )

    # First, try to get version from git tag
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        version = version.lstrip("v")

        # Write version to file for isolated builds
        with open(version_file, "w") as f:
            f.write(f'__version__ = "{version}"\n')

        return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Second, try to read from version file (for isolated builds)
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")

    # Fall back to default version
    return "0.0.36"


# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Bestatic',
    version=get_version(),
    author='Tatsat Banerjee',
    download_url='https://github.com/tatsatb/bestatic/releases/latest',
    url='https://www.bestaticpy.com/',
    packages=find_packages(),
    package_data={
        '': ['README.md', 'LICENSE', 'requirements.txt', 'bestatic.yaml']
    },
    include_package_data=True,
    install_requires=[
        'beautifulsoup4==4.14.3',
        'chardet==5.2.0',
        'Jinja2==3.1.6',
        'Markdown==3.10',
        'markdown-include==0.8.1',
        'MarkupSafe==3.0.3',
        'mkdocs-material==9.7.1',
        'Pygments==2.19.2',
        'python-frontmatter==1.1.0',
        'PyYAML==6.0.3',
        'soupsieve==2.8.1',
        'text-unidecode==1.3',
        'tomli==2.3.0',
        'pytz==2025.2',
        'feedgen==1.0.0',
        'markdown-customblocks==1.5.4',
        'pymdown-extensions==10.19.1',
        'watchdog==6.0.0',
        'Pillow==12.0.0',
        'python-magic-bin==0.4.14; sys_platform == "win32"',
        'python-magic==0.4.27; sys_platform != "win32"'
    ],
    extras_require={
        'dev': [
            'pytest==9.0.2',
            'pytest-cov==3.0.0',]
    },
    python_requires=">=3.10",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Operating System :: OS Independent'
    ],
    license='GPL-3.0-or-later',
    entry_points={
        'console_scripts': [
            'bestatic = bestatic.bestatic:main'
        ]
    },
    description="A simple but really powerful static-site generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='static-site-generator documentation blog website markdown jinja2',
    project_urls={
        'Bug Reports': 'https://github.com/tatsatb/bestatic/issues',
        'Source': 'https://github.com/tatsatb/bestatic',
        'Documentation': 'https://www.bestaticpy.com/docs/',
    },
)
