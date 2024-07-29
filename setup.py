from setuptools import setup, find_packages
from bestatic import __version__

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='Bestatic',
    version=__version__,
    author='Tatsat Banerjee',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4 == 4.12.3',
        'Jinja2 == 3.1.4',
        'Markdown == 3.5.2',
        'MarkupSafe == 2.1.5',
        'Pygments == 2.17.2',
        'python-frontmatter == 1.1.0',
        'PyYAML == 6.0.1',
        'soupsieve == 2.5',
        'text-unidecode == 1.3',
        'tomli == 2.0.1',
        'tomli_w == 1.0.0',
        'pytz == 2024.1',
        'feedgen == 1.0.0',
        'markdown-customblocks == 1.4.1',
        'pymdown-extensions == 10.7.1',
        'watchdog == 4.0.1'
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'bestatic = bestatic.bestatic:main'
        ]
    },
    description="A simple but powerful static-site generator",
    long_description=description,
    long_description_content_type="text/markdown",
)
