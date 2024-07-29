import os
import datetime
import frontmatter


def newpost(filepath):
    post_dict = {'title': "This is a sample post",
                 'date': datetime.datetime.now().strftime("%B %d, %Y"),
                 'tags': "tag1, tag2",
                 'description': "This is sample description or summary of a post",
                 'slug': "sample slug post"
                 }

    markdown_content_post = ("This is an example post content in simple markdown. Please replace this with content of "
                             "your choice. ")

    post = frontmatter.Post(markdown_content_post, **post_dict)
    os.makedirs("posts", exist_ok=True)

    # Split the pathname to get filename and directory path
    filename = os.path.basename(filepath)
    directory_path = os.path.dirname(filepath)
    os.makedirs(os.path.join("posts", directory_path), exist_ok=True)

    with open(f'posts/{filepath}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))


def newpage(filepath):
    page_dict = {'title': "This is a sample page",
                 'description': "This is sample description or summary of a page",
                 'slug': "sample slug page"
                 }

    markdown_content_post = ("This is an example page content in simple markdown. Please replace this with content of "
                             "your choice. ")

    page = frontmatter.Post(markdown_content_post, **page_dict)
    os.makedirs("pages", exist_ok=True)

    # Split the pathname to get filename and directory path
    filename = os.path.basename(filepath)
    directory_path = os.path.dirname(filepath)
    os.makedirs(os.path.join("pages", directory_path), exist_ok=True)

    with open(f'pages/{filepath}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(page))
