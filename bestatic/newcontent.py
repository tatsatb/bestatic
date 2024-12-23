import os
import datetime
import frontmatter


def newpost(filepath, time_format):


    # Split the pathname to get filename and directory path
    filename = os.path.basename(filepath)
    directory_path = os.path.dirname(filepath)
    os.makedirs(os.path.join("posts", directory_path), exist_ok=True)

    post_dict = {'title': "This is a sample post",
                 'date': datetime.datetime.now().strftime(time_format),
                 'tags': "sample-tag-1, sample-tag-2",
                 'description': "This is sample description or summary of a post",
                 'slug': f"{filename}"
                 }

    markdown_content_post = ("This is an example post content in simple markdown. Please replace this with content of "
                             "your choice. ")

    post = frontmatter.Post(markdown_content_post, **post_dict)
    os.makedirs("posts", exist_ok=True)



    with open(f'posts/{filepath}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(post))


def newpage(filepath):


    # Split the pathname to get filename and directory path
    filename = os.path.basename(filepath)
    directory_path = os.path.dirname(filepath)
    os.makedirs(os.path.join("pages", directory_path), exist_ok=True)

    page_dict = {'title': "This is a sample page",
                 'description': "This is sample description or summary of a page",
                 'slug': f"{filename}"
                 }

    markdown_content_post = ("This is an example page content in simple markdown. Please replace this with content of "
                             "your choice. ")

    page = frontmatter.Post(markdown_content_post, **page_dict)
    os.makedirs("pages", exist_ok=True)



    with open(f'pages/{filepath}.md', 'w', encoding='utf-8') as f:
        f.write(frontmatter.dumps(page))
