# Bestatic

### [Install from PyPI](https://pypi.org/project/Bestatic/) | [Demo](https://demo.bestaticpy.com/) with "Amazing" theme

Bestatic is a static-site generator, written in Python and Jinja2 templating engine. 
It is truly minimal, yet fully-featured. Like every other static-site generator,
it can generate a complete website by processing a bunch of markdown files. As a result, 
it eliminates the need for server-side programming or databases. The site _Bestatic_ generates
in ````_output```` folder can be served from any web server or host (or even GitHub pages or GitLab pages). 

Some salient features of _Bestatic_ that are probably worth highlighting:

-  Blog-aware. You can create your blog/news page along with your website and expect all the standard 
good stuff. Posts will be listed in the reverse chronological order. You can also control number of posts per page. 

-  Tags and URL customizations are supported for the posts out-of-the-box. 

-  Different description tag for each page of the website (SEO friendly).

-  `LaTeX` support is available out-of-the-box.

-  Search functionality has been implemented using `Fuse.js` library which enables client-side fuzzy
(approximate string matching) search. No action is required from user-end: Whenever the user adds new content and 
complies the website, it automatically generates a new search index. 

-  Pre-built site themes (created using Jinja2 template engine, more will be added later; you can add your own as well). 

-  Syntax-highlighting for codes is available out-of-the-box.

-  Disqus and Giscus comments are fully supported.

-  A simple web server has been included which enables viewing all the changes in the site instantly. 

-  Guided quick-start from the command-line. 


-  Configurable via a `config.yaml` file.

## Installation

There are several ways to install _Bestatic_. The [GitHub repo](https://github.com/tatsatb/bestatic) will be updated 
with more details. For now, please use pip/pipx for installation.

### Using pipx (recommended)

If you have not already installed it, please install pipx first using 
[official documentation](https://pipx.pypa.io/stable/installation/), as per your OS platform. Next, just use this
following command to install Bestatic. 

    pipx install Bestatic

### Using pip

If you are on Linux (Ubuntu/Debian) please use this: 

    sudo apt update && sudo apt upgrade
    sudo apt install python3-venv
    python3 -m venv ~/.virtualenvs/bestatic
    source ~/.virtualenvs/bestatic/bin/activate
    pip install Bestatic


Similar commands can be used to create virtual environment in Windows or mac OS. Bestatic can also be installed
inside a conda environment. 

Make sure to have a `config.yaml` file and `themes` folder in the working directory (as an example you can use the ones available in this repo). You can also run `bestatic quickstart` to create a config.yaml file from scratch and to build a site.   

