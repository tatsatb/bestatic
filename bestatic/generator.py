def generator(**config):
    import os
    from datetime import datetime
    from jinja2 import Environment, PackageLoader
    from markdown import markdown
    from markdown.extensions import codehilite
    from markdown.extensions.toc import slugify
    import frontmatter
    import shutil
    import copy
    import re
    from bs4 import BeautifulSoup
    from feedgen.feed import FeedGenerator
    import pytz
    import json
    from bestatic import bestaticSitemap

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
            self.parse_data()

        def parse_data(self):
            with open(self.path_of_md, 'r', encoding='utf-8') as f:
                self.content = markdown(f.read(), extensions=[
                    "meta", "attr_list", codehilite.CodeHiliteExtension(linenos="inline"), "fenced_code"])
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

    siteURL = config["siteURL"] if config and "siteURL" in config else "https://example.org"
    site_title = config["title"] if config and "title" in config else "A Demo Site for Bestatic"
    site_description = config["description"] if config and "description" in config else "A Demo Site for Bestatic"
    theme_name = config["theme"] if config and "theme" in config else "Amazing"
    rss_feed = config["rss_feed"] \
        if config and "rss_feed" in config else True
    current_directory = os.getcwd()

    shutil.rmtree(os.path.join(current_directory, "_output")) if os.path.exists(
        os.path.join(current_directory, "_output")) else None

    working_directory = os.path.join(current_directory, "themes", theme_name)
    format_files = False if config and "ugly_url" in config and config["ugly_url"] is True else True
    extension = "" if format_files else ".html"
    json_extension = ""

    source = os.path.join(working_directory, "static")
    destination = os.path.join(current_directory, "_output", "static")

    try:
        shutil.copytree(source, destination, dirs_exist_ok=True)
    except shutil.SameFileError:
        print("Source and destination represents the same file.")
    except PermissionError:
        print("Permission denied.")

    POSTS = {}
    PAGES = {}

    if os.path.isdir('posts') and len(os.listdir('posts')):
        for post_counter in os.listdir('posts'):
            input_post_path = os.path.join('posts', post_counter)
            POSTS[post_counter] = Parsing(input_post_path)

    if os.path.isdir('pages') and len(os.listdir('pages')):
        for page_counter in os.listdir('pages'):
            input_page_path = os.path.join('pages', page_counter)
            PAGES[page_counter] = Parsing(input_page_path)

    navigation_items = {key: {"title": value.title, "slug": value.slug} for key, value in PAGES.items() if
                        key != "404.md"}

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
                                          typeof="home", extension=extension, navi=navigation_items)
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

            output_page_path = '_output/{slug}{extension}'.format(slug=PAGES[page].slug, extension=extension)

            if PAGES[page].metadata['slug'] == 404 and error_template:
                page_final = error_template.render(title=site_title, description=site_description,
                                                   typeof="pages", extension=extension, navi=navigation_items)
            else:
                page_final = page_template.render(title=site_title, description=site_description,
                                                  page=PAGES[page], typeof="pages", extension=extension,
                                                  navi=navigation_items)

            os.makedirs(os.path.dirname(output_page_path), exist_ok=True)
            with open(output_page_path, 'w', encoding="utf-8") as file:
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
        # POSTS_SORTED = {}
        POSTS_SORTED = {item: POSTS[item] for item in POSTS_SORTED_LIST}
        # for item in POSTS_SORTED_LIST:
        #     POSTS_SORTED[item] = POSTS[item]

        POSTS_SORTED_temp = copy.deepcopy(POSTS_SORTED)
        POSTS_SORTED_temp.pop(next(iter(POSTS_SORTED_temp)))

        next_slugs_list = []
        for post in POSTS_SORTED_temp:
            next_slugs_list.append(POSTS_SORTED[post].metadata["slug"])

        prev_slug = None

        user_input_n = config['number_of_pages'] if config and "number_of_pages" in config else 4
        disqus = config["disqus"]["disqusShortname"] \
            if config and "disqus" in config and config["disqus"]["enabled"] is True else False

        for ii, (post, value) in enumerate(POSTS_SORTED.items()):
            output_post_path = '_output/post/{slug}{extension}'.format(slug=POSTS_SORTED[post].slug,
                                                                       extension=extension)
            tags_in_post_individual = POSTS_SORTED[post].tags
            next_slug = next_slugs_list[ii] if ii < len(next_slugs_list) else None
            post_final = post_template.render(title=site_title, description=site_description,
                                              post=POSTS_SORTED[post], typeof="posts", next_slug=next_slug,
                                              prev_slug=prev_slug,
                                              disqus=disqus, extension=extension, navi=navigation_items)
            prev_slug = POSTS_SORTED[post].slug
            os.makedirs(os.path.dirname(output_post_path), exist_ok=True)
            with open(output_post_path, 'w', encoding="utf-8") as file:
                file.write(post_final)

        split_dicts = split_dict_into_n(POSTS_SORTED, user_input_n)

        for jj in range(len(split_dicts)):
            list_final = list_template.render(title=site_title, description=site_description,
                                              post=split_dicts[jj], page_index=jj, page_range=len(split_dicts),
                                              typeof="lists",
                                              extension=extension, navi=navigation_items)
            paginator = "_output/posts" + str(jj + 1) + extension if jj != 0 else "_output/posts" + extension
            with open(paginator, 'w', encoding="utf-8") as file:
                file.write(list_final)

        Tag_list = [POSTS_SORTED[item].metadata["tags"] for item in POSTS_SORTED]
        Tag_list_temp = " ".join(Tag_list)

        Tag_list_final = isolate_tags(Tag_list_temp)

        for tags in Tag_list_final:
            output_tag_path = f'_output/post/tags/{tags}{extension}'
            POSTS_tag = {}
            for item in POSTS_SORTED:
                tags_in_post_correct = POSTS_SORTED[item].tags

                if tags in tags_in_post_correct:
                    POSTS_tag[item] = POSTS[item]

            tag_page_final = tags_template.render(title=site_title, description=site_description,
                                                  post=POSTS_tag, typeof="tags", tags=tags, extension=extension,
                                                  navi=navigation_items)
            os.makedirs(os.path.dirname(output_tag_path), exist_ok=True)
            with open(output_tag_path, 'w', encoding="utf-8") as file:
                file.write(tag_page_final)

    json_combined_dict = {}

    json_dict_post = {key: {'title': value.title, 'text': value.text, 'slug': f"post/{value.slug}"} for key, value in
                      POSTS.items()} if post_template else {}

    json_dict_page = {key: {'title': value.title, 'text': value.text, 'slug': value.slug} for key, value in
                      PAGES.items() if key != "404.md"} if page_template else {}

    json_combined_dict = {**json_dict_post, **json_dict_page}

    if json_combined_dict:
        result_dict = [{'uri': f"{value['slug']}{json_extension}", 'title': value['title'], 'content': value['text']}
                       for
                       value
                       in
                       json_combined_dict.values()]

        result_dict_post = [
            {'uri': f"../{value['slug']}{json_extension}", 'title': value['title'], 'content': value['text']} for
            value in
            json_combined_dict.values()]

        result_dict_tags = [
            {'uri': f"../../{value['slug']}{json_extension}", 'title': value['title'], 'content': value['text']} for
            value in
            json_combined_dict.values()]

        json_data_processing(result_dict, f'_output/index.json')

        if post_template:
            json_data_processing(result_dict_post, f'_output/post/index.json')
            json_data_processing(result_dict_tags, f'_output/post/tags/index.json')

    bestaticSitemap.generate_sitemap(siteURL, "_output")

    timezone = pytz.timezone('UTC')

    if post_template and rss_feed is True:
        rss_dict_post = {
            key: {'title': value.title, 'text': value.text, 'slug': f"post/{value.slug}",
                  'date': datetime.strptime(value.metadata["date"], "%B %d, %Y")} for
            key, value in
            reversed(POSTS_SORTED.items())} if post_template else {}

        posts_dict = [
            {'uri': f"{siteURL}/{value['slug']}{json_extension}", 'title': value['title'], 'content': value['text'],
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

        # Save the feed to a file (optional)
        with open('_output/index.rss', 'wb') as rss_file:
            rss_file.write(rss_feed)

    return None


if __name__ == '__main__':
    generator()
