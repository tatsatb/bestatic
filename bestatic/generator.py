def generator(**config):
    import os
    from datetime import datetime
    from jinja2 import Environment, PackageLoader
    from markdown import markdown
    from markdown.extensions import codehilite
    from markdown.extensions.toc import slugify
    from pymdownx import emoji
    import frontmatter
    import shutil
    import copy
    import re
    from bs4 import BeautifulSoup
    from feedgen.feed import FeedGenerator
    import pytz
    import json
    from bestatic import bestaticSitemap

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
            self.parse_data()
            self.path_data()

        def parse_data(self):
            with open(self.path_of_md, 'r', encoding='utf-8') as f:
                self.content = markdown(f.read(), extensions=[
                    "meta", "attr_list", "tables", codehilite.CodeHiliteExtension(linenos="inline"), "fenced_code",
                    "customblocks", 'pymdownx.emoji'], extension_configs={
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
                })

                f.seek(0)
                self.metadata = frontmatter.load(f).metadata
                plain_text = ''.join(BeautifulSoup(self.content, 'html.parser').findAll(string=True))
                self.text = plain_text
                self.summary = plain_text[:250] + "..." if len(plain_text) > 250 else plain_text
                self.title = self.metadata["title"]
                self.slug = self.metadata["slug"] if "slug" in self.metadata else slugify(self.title, separator="-")
                if "tags" in self.metadata:
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
    enable_inject_tag = config ["enable_inject_tag"] if config and "enable_inject_tag" in config else True
    current_directory = os.getcwd()

    shutil.rmtree(os.path.join(current_directory, "_output")) if os.path.exists(
        os.path.join(current_directory, "_output")) else None

    working_directory = os.path.join(current_directory, "themes", theme_name)

    source_theme = os.path.join(working_directory, "static")
    destination_theme = os.path.join(current_directory, "_output", "static")

    source = os.path.join(current_directory, "static-content")
    destination = os.path.join(current_directory, "_output", "static-content")

    copy_if_exists(source_theme, destination_theme)
    copy_if_exists(source, destination)


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

    env.trim_blocks = True
    env.lstrip_blocks = True

    home_template = None
    page_template = None
    post_template = None
    error_template = None
    list_template = None
    tags_template = None

    if os.path.exists(os.path.join(working_directory, "templates", "home.html.jinja2")):
        home_template = env.get_template('home.html.jinja2')
        home_final = home_template.render(title=site_title, description=site_description,
                                          typeof="home")
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

    if page_template:
        for page in PAGES:

            output_page_path = f"_output/{PAGES[page].path_info}/{PAGES[page].slug}"

            if PAGES[page].metadata['slug'] == 404 and error_template:
                page_final = error_template.render(title=site_title, description=site_description,
                                                   typeof="pages")
            else:
                if "template" in PAGES[page].metadata:
                    page_template = env.get_template(PAGES[page].metadata['template'])
                    page_final = page_template.render(title=site_title, description=site_description,
                                                      page=PAGES[page], typeof="pages")
                else:
                    page_template = env.get_template('page.html.jinja2')
                    page_final = page_template.render(title=site_title, description=site_description,
                                                      page=PAGES[page], typeof="pages")

            if PAGES[page].metadata['slug'] and PAGES[page].metadata['slug'] == "index.html":
                with open(f"_output/index.html", "w", encoding="utf-8") as file:
                    file.write(page_final)
            else:
                if not os.path.exists(output_page_path):
                    os.makedirs(output_page_path, exist_ok=True)
                with open(f"{output_page_path}/index.html", 'w', encoding="utf-8") as file:
                    file.write(page_final)

    if os.path.isdir('posts') and len(os.listdir('posts')):
        try:
            post_template = env.get_template('post.html.jinja2')
            list_template = env.get_template('list.html.jinja2')
            tags_template = env.get_template('taglist.html.jinja2')
        except FileNotFoundError:
            raise Exception("The 'post', 'list', and 'taglist' template must exist in the templates directory of "
                            "theme root directory to process the blog/posts/news items.")
    else:
        pass

    if post_template:

        POSTS_SORTED_LIST = sorted(POSTS, key=lambda sorter: datetime.strptime(POSTS[sorter].metadata["date"],
                                                                               "%B %d, %Y"), reverse=True)
        POSTS_SORTED = {item: POSTS[item] for item in POSTS_SORTED_LIST}


        POSTS_SORTED_temp = copy.deepcopy(POSTS_SORTED)
        POSTS_SORTED_temp.pop(next(iter(POSTS_SORTED_temp)))

        next_slugs_list = []
        for post in POSTS_SORTED_temp:
            next_slugs_list.append(f"{POSTS[post].path_info}/{POSTS_SORTED[post].slug}")

        prev_slug = None

        user_input_n = config['number_of_pages'] if config and "number_of_pages" in config else 1



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


        for ii, (post, value) in enumerate(POSTS_SORTED.items()):
            output_post_path = f"_output/post/{POSTS[post].path_info}/{POSTS_SORTED[post].slug}"

            tags_in_post_individual = POSTS_SORTED[post].tags
            next_slug = next_slugs_list[ii] if ii < len(next_slugs_list) else None
            post_final = post_template.render(title=site_title, description=site_description,
                                              post=POSTS_SORTED[post], typeof="posts", next_slug=next_slug,
                                              prev_slug=prev_slug,
                                              disqus=disqus, giscus=giscus)
            prev_slug = f"{POSTS[post].path_info}/{POSTS_SORTED[post].slug}"

            if not os.path.exists(output_post_path):
                os.makedirs(output_post_path, exist_ok=True)
            with open(f"{output_post_path}/index.html", 'w', encoding="utf-8") as file:
                file.write(post_final)

        split_dicts = split_dict_into_n(POSTS_SORTED, user_input_n)

        for jj in range(len(split_dicts)):
            list_final = list_template.render(title=site_title, description=site_description,
                                              post=split_dicts[jj], page_index=jj, page_range=len(split_dicts),
                                              typeof="lists")
            paginator = "_output/posts" + str(jj + 1) if jj != 0 else "_output/posts"

            if not os.path.exists(paginator):
                os.makedirs(paginator, exist_ok=True)
            with open(f"{paginator}/index.html", 'w', encoding="utf-8") as file:
                file.write(list_final)

        if homepage_type == "list":
            shutil.move("_output/posts/index.html", "_output/index.html")

        Tag_list = [POSTS_SORTED[item].metadata["tags"] for item in POSTS_SORTED if "tags" in POSTS_SORTED[item].metadata]
        Tag_list_temp = " ".join(Tag_list)

        Tag_list_final = isolate_tags(Tag_list_temp)

        for tags in Tag_list_final:
            output_tag_path = f'_output/post/tags/{tags}'
            POSTS_tag = {}
            for item in POSTS_SORTED:
                tags_in_post_correct = POSTS_SORTED[item].tags

                if tags_in_post_correct is not None and tags in tags_in_post_correct:
                    POSTS_tag[item] = POSTS[item]

            tag_page_final = tags_template.render(title=site_title, description=site_description,
                                                  post=POSTS_tag, typeof="tags", tags=tags)

            if not os.path.exists(output_tag_path):
                os.makedirs(output_tag_path, exist_ok=True)
            with open(f"{output_tag_path}/index.html", 'w', encoding="utf-8") as file:
                file.write(tag_page_final)

    json_combined_dict = {}

    json_dict_post = {key: {'title': value.title, 'text': value.text,
                            'slug': f"post/{value.path_info}/{value.slug}" if value.path_info else f"post/{value.slug}"} for
                      key, value in
                      POSTS.items()} if post_template else {}

    json_dict_page = {key: {'title': value.title, 'text': value.text,
                            'slug': f"{value.path_info}/{value.slug}" if value.path_info else f"{value.slug}"} for
                      key, value in
                      PAGES.items() if key != "404.md"} if page_template else {}

    json_combined_dict = {**json_dict_post, **json_dict_page}

    if json_combined_dict:
        result_dict = [{'uri': f"{value['slug']}", 'title': value['title'], 'content': value['text']}
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

    timezone = pytz.timezone('UTC')

    if post_template and rss_feed is True:
        rss_dict_post = {
            key: {'title': value.title, 'text': value.text,
                  'slug': f"post/{value.path_info}/{value.slug}" if value.path_info else f"{value.slug}",
                  'date': datetime.strptime(value.metadata["date"], "%B %d, %Y")} for
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
        fg.link(href=siteURL + "/posts", rel='alternate')
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

    if enable_inject_tag == True:
        with open("_output/index.html", 'r', encoding="utf-8") as fi:
            content = fi.read()

        if re.search(r'<meta name="generator" content="Bestatic"/>', content):
            pass
        else:
            head_start_pattern = r'<head>'
            if head_start_pattern == -1:
                pass
            else:
                new_content = re.sub(head_start_pattern, head_start_pattern + '\n\t\t<meta name="generator" content="Bestatic"/>', content)

                with open("_output/index.html", 'w', encoding="utf-8") as file:
                    file.write(new_content)
    else:
        pass

    return None


if __name__ == '__main__':
    generator()
