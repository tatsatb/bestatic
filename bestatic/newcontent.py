import os
import datetime
import frontmatter


def newpost(filename):
    post_dict = {'title': "This is a sample post",
                 'date': datetime.datetime.now().strftime("%B %d, %Y"),
                 'tags': "tag1, tag2",
                 'description': "This is sample description or summary of a post",
                 'slug': "enter something here to generate URL or delete this 'slug' field to autogenerate"
                 }

    markdown_content_post = ("This is an example post content in simple markdown. Please replace this with content of "
                             "your choice. ")

    post = frontmatter.Post(markdown_content_post, **post_dict)
    os.makedirs("posts", exist_ok=True)

    with open(f'posts/{filename}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))


def newpage(filename):
    page_dict = {'title': "This is a sample page",
                 'description': "This is sample description or summary of a page",
                 'slug': "enter something here to generate URL or delete this 'slug' field to autogenerate"
                 }

    markdown_content_post = ("This is an example page content in simple markdown. Please replace this with content of "
                             "your choice. ")

    page = frontmatter.Post(markdown_content_post, **page_dict)
    os.makedirs("pages", exist_ok=True)

    with open(f'pages/{filename}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(page))
