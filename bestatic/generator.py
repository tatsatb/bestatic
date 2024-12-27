def generator(**config):
    import os
    from datetime import datetime
    from pathlib import Path
    from jinja2 import Environment, PackageLoader
    from markdown import markdown
    from markdown.extensions.toc import slugify
    from pymdownx import emoji
    import frontmatter
    import yaml 
    import shutil
    import copy
    import re
    import warnings
    import chardet
    from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
    from feedgen.feed import FeedGenerator
    import pytz
    import json
    from bestatic import bestaticSitemap
    from bestatic.shortcodes import ShortcodeProcessor


    def copy_if_exists(source, destination):
        if os.path.exists(source):
            try:
                shutil.copytree(source, destination, dirs_exist_ok=True)
            except shutil.SameFileError:
                print("Source and destination represent the same file.")
            except PermissionError:
                print("Permission denied.")
        else:
            pass
        return None

    def isolate_tags(taglist):
        """Split taxonomy terms into list"""
        if isinstance(taglist, list):
            return taglist
        taglist_2 = re.split(r'\s|(?<!\d)[,.]|,.', taglist)
        taglist_3 = [tag for tag in taglist_2 if tag]
        taglist_final = list(set(taglist_3))
        return taglist_final

    def split_dict_into_n(d, n):
        """
        Splits a dictionary into n different dictionaries.

        Args:
            d (dict): The input dictionary.
            n (int): Number of dictionaries to split into.

        Returns:
            List[dict]: A list of n dictionaries.
        """
        # Calculate the chunk size for each sub-dictionary
        chunk_size = len(d) // n

        # Initialize an empty list to store the sub-dictionaries
        result = []

        # Iterate n times to create n sub-dictionaries
        for i in range(n):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size if i < n - 1 else len(d)
            sub_dict = dict(list(d.items())[start_idx:end_idx])
            result.append(sub_dict)

        return result

    def json_data_processing(dict_all, json_path):
        json_data_temp = json.dumps(dict_all, indent=2)
        with open(json_path, "w") as filej:
            filej.write(json_data_temp)
        return None

    def process_directory(directory, sitename):
        """Recursively processes files in a directory, replacing href, src, and url attributes."""
        
        # Process HTML files
        for path in Path(directory).rglob('*.html'):
            # Process href and src attributes
            pattern = r'(href|src)\s*=\s*"/'
            replacement = rf'\1="{sitename}/'
            
            # Add pattern for b-search-file-index
            pattern_search = r'b-search-file-index\s*=\s*"/'
            replacement_search = rf'b-search-file-index="{sitename}/'

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Apply both replacements
            new_content = re.sub(pattern, replacement, content)
            new_content = re.sub(pattern_search, replacement_search, new_content)

            with open(path, 'w', encoding="utf-8") as f:
                f.write(new_content)

        # Process CSS files
        for path in Path(directory).rglob('*.css'):
            with open(path, 'rb') as f:
                content = f.read()
                result = chardet.detect(content)
                encoding = result['encoding']
 

            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
                
                def replace_url(match):
                    quote = match.group(1) or ''  # Get quote type if present
                    path = match.group(2)
                    if quote:
                        # If quotes exist, use them
                        return f'url({quote}{sitename}{path}{quote})'
                    else:
                        # If no quotes, don't add any
                        return f'url({sitename}{path})'

                # Pattern matches: url(/path), url('/path'), and url("/path")
                pattern = r'url\(([\'"])?(/[^\'"\)]+)(?:\1)?\)'
                content = re.sub(pattern, replace_url, content)

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

    def process_searchindex(searchindex_path, sitename):

        pattern = r'"uri":\s*"/'
        replacement = rf'"uri": "{sitename}/'

        with open(searchindex_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = re.sub(pattern, replacement, content)

        with open(searchindex_path, 'w', encoding="utf-8") as f:
            f.write(new_content)

        pattern_2 = r'/index.json'
        replacement_2 = rf'{sitename}/index.json'


    def parse_sections(html_content):
        """Parse HTML content into sections based on headings with class 'splitsection'"""
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = []
        current_section = {'heading': None, 'content': [], 'index': 0}
        
        elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div'])
        section_index = 0
        
        for element in elements:
            if element.name.startswith('h') and 'splitsection' in element.get('class', []):
                if current_section['content']:
                    sections.append(current_section)
                section_index += 1
                current_section = {
                    'heading': element.get_text(),
                    'content': [],
                    'index': section_index
                }
            else:
                current_section['content'].append(str(element))
        
        if current_section['content']:
            sections.append(current_section)
            
        return sections    

    def load_all_taxonomy_yaml():
        """Load all taxonomy YAML files from _includes/yamls directory"""
        taxonomy_yamls = {}
        yaml_dir = os.path.join(current_directory, '_includes', 'yamls')
        if os.path.exists(yaml_dir):
            for yaml_file in os.listdir(yaml_dir):
                if yaml_file.endswith('.yaml'):
                    taxonomy_name = os.path.splitext(yaml_file)[0]
                    yaml_path = os.path.join(yaml_dir, yaml_file)
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        taxonomy_yamls[taxonomy_name] = yaml.load(f, Loader=yaml.Loader)
        return taxonomy_yamls


    class Parsing:
        def __init__(self, path_of_md):
            self.path_of_md = path_of_md
            self.metadata = None
            self.content = None
            self.summary = None
            self.tags = None
            self.katex = None
            self.text = None
            self.title = None
            self.slug = None
            self.path_info = None
            self.shortcode_processor = ShortcodeProcessor() if enable_shortcodes else None
            self.parse_data()
            self.path_data()

        def parse_data(self):

            warnings.filterwarnings('ignore', category=MarkupResemblesLocatorWarning)

            with open(self.path_of_md, 'r', encoding='utf-8') as f:
                content = f.read()
                # Only process shortcodes if enabled
                if self.shortcode_processor:
                    content = self.shortcode_processor.process_content(content)
                self.content = markdown(content, extensions=markdown_extensions, extension_configs=markdown_configs)
                f.seek(0)
                self.metadata = frontmatter.load(f).metadata
                initial_clean = BeautifulSoup(self.content, 'html.parser').get_text()
                plain_text = BeautifulSoup(initial_clean, 'html.parser').get_text(separator=' ').strip()
                self.text = plain_text
                self.summary = plain_text[:summary_length] + "..." if len(plain_text) > summary_length else plain_text
                self.title = self.metadata["title"]
                self.slug = self.metadata["slug"] if "slug" in self.metadata else slugify(self.title, separator="-")
                if "tags" in self.metadata and self.metadata["tags"] is not None:
                    self.tags = isolate_tags(self.metadata["tags"])
                else:
                    None
                if "katex" in self.metadata and "katex":
                    self.katex = True

        def path_data(self):
            self.path_info = os.path.dirname(self.path_of_md)
            parts = self.path_info.split(os.path.sep)
            filtered_parts = parts[1:]
            self.path_info = os.path.sep.join(filtered_parts)

    siteURL = config["siteURL"] if config and "siteURL" in config else "https://example.org"
    site_title = config["title"] if config and "title" in config else "A Demo Site for Bestatic"
    site_description = config["description"] if config and "description" in config else "A Demo Site for Bestatic"
    theme_name = config["theme"] if config and "theme" in config else "Amazing"
    rss_feed = config["rss_feed"] \
        if config and "rss_feed" in config else True
    homepage_type = config ["homepage_type"] if config and "homepage_type" in config else "default"
    time_format = config["time_format"] if config and "time_format" in config else "%B %d, %Y"
    timezone_name = config["timezone"] if config and "timezone" in config else "UTC"
    summary_length = config["summary_length"] if config and "summary_length" in config else 250
    nav = config["nav"] if config and "nav" in config else None
    enable_inject_tag = config ["enable_inject_tag"] if config and "enable_inject_tag" in config else True
    post_directory_singular = config["post_directory"]["singular"] if config and "post_directory" in config else "post"
    post_directory_plural = config["post_directory"]["plural"] if config and "post_directory" in config else "posts"
    user_input_n = config['number_of_pages'] if config and "number_of_pages" in config else 1
    posts_in_page = config['include_post_in_pages'] if config and "include_post_in_pages" in config else False
    enable_shortcodes = config["SHORTCODES"] if config and "SHORTCODES" in config else False
    

    default_extensions = [
    "meta", 
    "attr_list", 
    "tables",
    "fenced_code",
    "customblocks", 
    "pymdownx.emoji",
    "codehilite"
    ]

    default_configs = {
        "pymdownx.emoji": {
            "emoji_index": emoji.twemoji,
            "emoji_generator": emoji.to_svg,
            "alt": "short",
            "options": {
                "attributes": {
                    "align": "absmiddle",
                    "height": "50px",
                    "width": "50px"
                },
            },
        },
        "codehilite": {
            "linenos": "table"
        },
    }


    # Process markdown settings
    if config and "markdown" in config:
        if config["markdown"].get("markdown_replace", False):
            markdown_extensions = config["markdown"].get("extensions", [])
            markdown_configs = config["markdown"].get("extension_configs", {})
        else:
            markdown_extensions = default_extensions.copy()
            markdown_configs = default_configs.copy()
            if "extensions" in config["markdown"]:
                markdown_extensions.extend(config["markdown"]["extensions"])
            if "extension_configs" in config["markdown"]:
                markdown_configs.update(config["markdown"]["extension_configs"])
    else:
        markdown_extensions = default_extensions
        markdown_configs = default_configs    
   

    
    
    
    project_site = config["projectsite"] if config and "projectsite" in config else None



    current_directory = os.getcwd()

    shutil.rmtree(os.path.join(current_directory, "_output")) if os.path.exists(
        os.path.join(current_directory, "_output")) else None

    working_directory = os.path.join(current_directory, "themes", theme_name)

    source_theme = os.path.join(working_directory, "static")
    destination_theme = os.path.join(current_directory, "_output", "static")

    source = os.path.join(current_directory, "static-content")
    destination = os.path.join(current_directory, "_output", "static-content")

    source_root_import = os.path.join(current_directory, "root-import")
    destination_root_import = os.path.join(current_directory, "_output")

    copy_if_exists(source_theme, destination_theme)
    copy_if_exists(source, destination)
    copy_if_exists(source_root_import, destination_root_import)


    if config and "comments" in config and config["comments"]["enabled"] is True:
        if config["comments"]["system"] == "giscus":
            giscus = config["comments"]["comment_system_id"]
            disqus = False
        elif config["comments"]["system"] == "disqus":
            disqus = config["comments"]["comment_system_id"]
            giscus = False
        else:
            giscus = False
            disqus = False
    else:
        giscus = False
        disqus = False    



    POSTS = {}
    PAGES = {}

    if os.path.isdir('posts') and len(os.listdir('posts')):
        for root, directories, files in os.walk('posts'):
            for filename in files:
                input_post_path = os.path.join(root, filename)
                POSTS[filename] = Parsing(input_post_path)

    if os.path.isdir('pages') and len(os.listdir('pages')):
        for root, directories, files in os.walk('pages'):
            for filename in files:
                input_page_path = os.path.join(root, filename)
                PAGES[filename] = Parsing(input_page_path)

    env = Environment(loader=PackageLoader("bestatic.generator", os.path.join(working_directory, "templates")))
    
    def md_filter(text):
        return markdown(text, extensions=markdown_extensions, extension_configs=markdown_configs)
    
    env.filters['markdown'] = md_filter
    env.trim_blocks = True
    env.lstrip_blocks = True

    home_template =  None
    page_template = None
    post_template = None
    error_template = None
    list_template = None
    tags_template = None

    if os.path.exists(os.path.join(working_directory, "templates", "home.html.jinja2")):
        home_template = env.get_template('home.html.jinja2')
        home_final = home_template.render(title=site_title, description=site_description, nav=nav)
        with open(f"_output/index.html", "w", encoding="utf-8") as file:
            file.write(home_final)

    if os.path.isdir('pages') and len(os.listdir('pages')):
        try:
            page_template = env.get_template('page.html.jinja2')
        except FileNotFoundError:
            raise Exception(
                "The 'page.html.jinja2' template must exist in the theme directory to process static pages.")

    if os.path.exists(os.path.join(working_directory, "templates", "404.html.jinja2")):
        error_template = env.get_template('404.html.jinja2')


    if os.path.isdir('posts') and len(os.listdir('posts')):
        try:
            post_template = env.get_template('post.html.jinja2')
            list_template = env.get_template('list.html.jinja2')
        except FileNotFoundError:
            raise Exception("The 'post' and 'list' template must exist in the root of the template directory of "
                            " the theme directory to process the blog/posts/news items.")
    else:
        pass


    if post_template:
        # Load all taxonomy YAML files
        all_taxonomy_yamls = load_all_taxonomy_yaml()

        POSTS_SORTED_LIST = sorted(POSTS, key=lambda sorter: datetime.strptime(POSTS[sorter].metadata["date"], time_format), reverse=True)
        POSTS_SORTED = {item: POSTS[item] for item in POSTS_SORTED_LIST}


        POSTS_SORTED_temp = copy.deepcopy(POSTS_SORTED)
        POSTS_SORTED_temp.pop(next(iter(POSTS_SORTED_temp)))

        next_slugs_list = []
        next_titles_list = []
        for post in POSTS_SORTED_temp:
            next_slugs_list.append(f"{POSTS[post].path_info}/{POSTS_SORTED[post].slug}")
            next_titles_list.append(POSTS_SORTED[post].title)

        prev_slug = None
        prev_title = None

        for ii, (post, value) in enumerate(POSTS_SORTED.items()):
            output_post_path = f"_output/{post_directory_singular}/{POSTS[post].path_info}/{POSTS_SORTED[post].slug}"

            tags_in_post_individual = POSTS_SORTED[post].tags
            next_slug = next_slugs_list[ii] if ii < len(next_slugs_list) else None
            next_title = next_titles_list[ii] if ii < len(next_titles_list) else None

            post_final = post_template.render(title=site_title, description=site_description, 
                                           post=POSTS_SORTED[post], 
                                           next_slug=next_slug, prev_slug=prev_slug,
                                           next_title=next_title, prev_title=prev_title,
                                           taxonomy_yamls=all_taxonomy_yamls, 
                                           post_directory_singular=post_directory_singular, 
                                           post_directory_plural=post_directory_plural, 
                                           disqus=disqus, giscus=giscus, nav=nav)

            prev_slug = f"{POSTS[post].path_info}/{POSTS_SORTED[post].slug}"
            prev_title = POSTS_SORTED[post].title


            if "slug" in POSTS_SORTED[post].metadata and POSTS_SORTED[post].metadata["slug"] == "index.html":
                with open(f"_output/index.html", "w", encoding="utf-8") as file:
                    file.write(post_final)
            else:
                if not os.path.exists(output_post_path):
                    os.makedirs(output_post_path, exist_ok=True)
                with open(f"{output_post_path}/index.html", 'w', encoding="utf-8") as file:
                    file.write(post_final)


        split_dicts = split_dict_into_n(POSTS_SORTED, user_input_n)

        for jj in range(len(split_dicts)):

            list_final = list_template.render(title=site_title, description=site_description, post_directory_singular=post_directory_singular, post_directory_plural=post_directory_plural, post=split_dicts[jj], page_index=jj, page_range=len(split_dicts), taxonomy_yamls=all_taxonomy_yamls, nav=nav)

            paginator = f"_output/{post_directory_plural}/{jj + 1}" if jj != 0 else f"_output/{post_directory_plural}"

            if not os.path.exists(paginator):
                os.makedirs(paginator, exist_ok=True)
            with open(f"{paginator}/index.html", 'w', encoding="utf-8") as file:
                file.write(list_final)

        if homepage_type == "list":
            shutil.move("_output/{post_directory_plural}/index.html", "_output/index.html")

        taxonomies = config["taxonomies"] if config and "taxonomies" in config else {
            "tags": {
                "taxonomy_template": "taglist.html.jinja2", 
                "taxonomy_directory": "tags"
            }
        }

        def process_taxonomy_terms(items_dict, taxonomy_name, taxonomy_config):
            """Process items for a given taxonomy (tags, categories, authors etc)"""
            # Try to load corresponding taxonomy YAML file if it exists
            taxonomy_yaml = None
            yaml_path = os.path.join(current_directory, '_includes', 'yamls', f'{taxonomy_name}.yaml')
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
                    taxonomy_yaml = yaml.load(yaml_file, Loader=yaml.Loader)

            terms_list = [items_dict[item].metadata[taxonomy_name] 
                        for item in items_dict 
                        if taxonomy_name in items_dict[item].metadata 
                        and items_dict[item].metadata[taxonomy_name] is not None]
            
            terms_list_temp = " ".join(str(t) for t in terms_list)
            terms_list_final = isolate_tags(terms_list_temp)
            
            template = env.get_template(taxonomy_config['taxonomy_template'])
            
            for term in terms_list_final:
                output_path = f'_output/{post_directory_singular}/{taxonomy_config["taxonomy_directory"]}/{term}'
                filtered_items = {}
                
                for item in items_dict:
                    item_terms = items_dict[item].metadata.get(taxonomy_name, [])
                    if item_terms:
                        terms = isolate_tags(item_terms)
                        if term in terms:
                            filtered_items[item] = items_dict[item]
                
                page_content = template.render(
                    title=site_title, 
                    description=site_description, 
                    post=filtered_items,
                    post_directory_singular=post_directory_singular, post_directory_plural=post_directory_plural, 
                    taxonomy_term=term,
                    taxonomy_name=taxonomy_name,
                    taxonomy_directory=taxonomy_config["taxonomy_directory"],
                    taxonomy_yaml=taxonomy_yaml,
                    nav=nav
                )
                
                if not os.path.exists(output_path):
                    os.makedirs(output_path, exist_ok=True)
                with open(f"{output_path}/index.html", 'w', encoding="utf-8") as file:
                    file.write(page_content)

        for taxonomy_name, taxonomy_config in taxonomies.items():
            process_taxonomy_terms(POSTS_SORTED, taxonomy_name, taxonomy_config)

    
    if page_template:
        for page in PAGES:

            output_page_path = f"_output/{PAGES[page].path_info}/{PAGES[page].slug}"

            sections = None
            if "section" in PAGES[page].metadata and PAGES[page].metadata['section'] is True:
                sections = parse_sections(PAGES[page].content)

            if "slug" in PAGES[page].metadata and PAGES[page].metadata['slug'] == 404 and error_template:
                page_final = error_template.render(title=site_title, description=site_description, nav=nav)
            else:
                POSTS_SORTED_in_page = POSTS_SORTED if posts_in_page else None                
                if "template" in PAGES[page].metadata:
                    page_template = env.get_template(PAGES[page].metadata['template'])
                    page_final = page_template.render(title=site_title, description=site_description, page=PAGES[page],  sections=sections, post_list = POSTS_SORTED_in_page,post_directory_singular=post_directory_singular, post_directory_plural=post_directory_plural, disqus=disqus, giscus=giscus, nav=nav)
                else:
                    page_template = env.get_template('page.html.jinja2')
                    page_final = page_template.render(title=site_title, description=site_description, page=PAGES[page],  sections=sections, post_list = POSTS_SORTED_in_page,
                    post_directory_singular=post_directory_singular, post_directory_plural=post_directory_plural, disqus=disqus, giscus=giscus, nav=nav)

            if "slug" in PAGES[page].metadata and PAGES[page].metadata['slug'] == "index.html":
                with open(f"_output/index.html", "w", encoding="utf-8") as file:
                    file.write(page_final)
            else:
                if not os.path.exists(output_page_path):
                    os.makedirs(output_page_path, exist_ok=True)
                with open(f"{output_page_path}/index.html", 'w', encoding="utf-8") as file:
                    file.write(page_final)
    
    
    json_combined_dict = {}

    json_dict_post = {key: {'title': value.title, 'text': value.text,
                            'slug': f"{post_directory_singular}/{value.path_info}/{value.slug}" if value.path_info else f"{post_directory_singular}/{value.slug}"} for
                      key, value in
                      POSTS.items()} if post_template else {}

    json_dict_page = {key: {'title': value.title, 'text': value.text,
                            'slug': f"{value.path_info}/{value.slug}" if value.path_info else f"{value.slug}"} for
                      key, value in
                      PAGES.items() if key != "404.md"} if page_template else {}

    json_combined_dict = {**json_dict_post, **json_dict_page}

    if json_combined_dict:
        result_dict = [{'uri': f"{value['slug']}", 'title': value['title'] if value['title'] else "Homepage", 'content': value['text']}
                   for
                   value
                   in
                   json_combined_dict.values()]

        result_dict_post = [
            {'uri': f"/{value['slug']}", 'title': value['title'], 'content': value['text']} for
            value in
            json_combined_dict.values()]

        result_dict_tags = [
            {'uri': f"/{value['slug']}", 'title': value['title'], 'content': value['text']} for
            value in
            json_combined_dict.values()]

        json_data_processing(result_dict, f'_output/index.json')

        if post_template:
            json_data_processing(result_dict_post, f'_output/index.json')

    bestaticSitemap.generate_sitemap(siteURL, "_output")

    timezone = pytz.timezone(timezone_name)

    if post_template and rss_feed is True:
        rss_dict_post = {
            key: {'title': value.title, 'text': value.text,
                  'slug': f"{post_directory_singular}/{value.path_info}/{value.slug}" if value.path_info else f"{value.slug}",
                  'date': datetime.strptime(value.metadata["date"], time_format)} for
            key, value in
            reversed(POSTS_SORTED.items())} if post_template else {}

        posts_dict = [
            {'uri': f"{siteURL}/{value['slug']}", 'title': value['title'], 'content': value['text'],
             'date': timezone.localize(value['date'])} for
            value
            in
            rss_dict_post.values()]

        fg = FeedGenerator()
        fg.title(site_title)
        fg.link(href=f"{siteURL}/{post_directory_plural}", rel='alternate')
        fg.description(site_description)

        # Add entries from the dictionary
        for entry_data in posts_dict:
            entry = fg.add_entry()
            entry.title(entry_data['title'])
            entry.description(entry_data['content'])
            entry.link(href=entry_data['uri'])
            entry.pubDate(entry_data['date'])

        # Generate the RSS feed
        rss_feed = fg.rss_str(pretty=True)

        with open('_output/index.rss', 'wb') as rss_file:
            rss_file.write(rss_feed)

    if project_site is not None:
        process_directory('_output', project_site)
        searchindex_path = os.path.join(current_directory, "_output", "index.json")
        process_searchindex(searchindex_path, project_site)

    if enable_inject_tag == True:
        with open("_output/index.html", 'r', encoding="utf-8") as fi:
            content = fi.read()

        if re.search(r'<meta name="generator" content="Bestatic" />', content):
            pass
        else:
            head_start_pattern = r'<head>'
            if head_start_pattern == -1:
                pass
            else:
                new_content = re.sub(head_start_pattern, head_start_pattern + '\n\t\t<meta name="generator" content="Bestatic" />', content)

                with open("_output/index.html", 'w', encoding="utf-8") as file:
                    file.write(new_content)
    else:
        pass

    return None


if __name__ == '__main__':
    generator()
