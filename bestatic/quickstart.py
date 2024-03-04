def quickstart(*theme):
    import os
    import tomli
    import tomli_w
    import frontmatter
    import datetime

    theme = "Amazing" if not theme else theme

    current_directory = os.getcwd()
    path = os.path.join(current_directory, "themes", theme)
    is_exist = os.path.exists(path)

    if not is_exist:
        raise FileNotFoundError(f"Theme directory does not exist! Please make sure a theme is present in themes"
                                f" directory")

    config_dict = {
        "title": input("Enter the title of the website: "),
        "description": input("Enter the description of the website: "),
        "theme": theme,
        "number_of_pages": 1,
        "ugly_url": False
    }

    while not config_dict["title"]:
        print("Title of the website cannot be empty! Please try again. ")
        config_dict["title"] = input("Enter the title of the website: ")

    while not config_dict["description"]:
        print("Description of the website cannot be empty! Please try again. ")
        config_dict["description"] = input("Enter the description of the website: ")

    output_file = "config.toml"

    # Write the dictionary to the TOML file
    with open(output_file, "wb") as f:
        tomli_w.dump(config_dict, f)

    with open("config.toml", mode="rb") as ft:
        config = tomli.load(ft)

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
            'description': "About the contact",
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
            f.write(frontmatter.dumps(post[item]))

    for item in page:
        with open(f'pages/{page[item].metadata["slug"]}.md', 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(page[item]))

    return config


if __name__ == '__main__':
    quickstart()
