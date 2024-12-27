def quickstart(*theme):
    import os
    import yaml
    import frontmatter
    import datetime


    theme = "Amazing" if not theme else theme

    current_directory = os.getcwd()
    path = os.path.join(current_directory, "themes", theme)
    is_exist = os.path.exists(path)

    if not is_exist:
        raise FileNotFoundError(f"Theme directory does not exist! Please make sure a proper theme is present in "
                                f"themes directory")

    config_dict = {
        "siteURL": "http://example.org",
        "theme": theme,
        "time_format": "%B %d, %Y",
        "number_of_pages": 1
    }

    fields = ["title", "description"]


    for field in fields:
        while True:
            value_field = input(f"Enter the {field} of the website: ")
            config_dict[field] = value_field
            if config_dict[field] == "":
                print(f"{field.capitalize()} cannot be empty! Please try again. ")
            else:
                break

    output_file = "bestatic.yaml"

    with open(output_file, "w") as f:
        yaml.dump(config_dict, f, sort_keys=False)

    with open("bestatic.yaml", mode="rb") as ft:
        config = yaml.safe_load(ft)

    post_dict = {
        "post1": {'title': 'My First Post',
                  'date': datetime.datetime.now().strftime("%B %d, %Y"),
                  'tags': "first, dolor-ipsum, sit, amet",
                  'description': "The first post of the Blog",
                  'slug': 'the-first-article'},
        "post2": {'title': 'My Second Post',
                  'date': datetime.datetime.now().strftime("%B %d, %Y"),
                  'tags': "good, dolor-ipsum, sit, great",
                  'description': "The second post of the Blog",
                  'slug': 'the-second-article'},
    }

    page_dict = {
        "page1": {
            'title': 'About',
            'description': "About the writer of this website",
            'slug': 'about'
        },
        "page2": {
            'title': 'Contact',
            'description': "How to contact the creators of this website",
            'slug': 'contact'
        }
    }

    # Create new markdown files
    markdown_content_post = "Well, hello there, world. This is an example post"
    markdown_content_page = "This is an example page. Thanks for visiting this website!"

    post = {}
    page = {}
    # Add the frontmatter to the markdown content
    for item in post_dict:
        post[item] = frontmatter.Post(markdown_content_post, **post_dict[item])

    for item in page_dict:
        page[item] = frontmatter.Post(markdown_content_page, **page_dict[item])
    # page = frontmatter.Post(markdown_content_page, **page_dict)

    os.makedirs("posts", exist_ok=True)
    os.makedirs("pages", exist_ok=True)

    # Save the updated contents to files
    for item in post:
        with open(f'posts/{post[item].metadata["slug"]}.md', 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post[item], sort_keys=False))

    for item in page:
        with open(f'pages/{page[item].metadata["slug"]}.md', 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(page[item], sort_keys=False))

    return config


if __name__ == '__main__':
    quickstart()
