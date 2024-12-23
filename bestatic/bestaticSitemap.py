import os
import datetime
import xml.etree.ElementTree as ET


def get_last_modified_time(file_path):
    file_path = os.path.join("_output", file_path, "index.html")
    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()


def find_single_index_folders(root_folder):
    matching_folders = []
    for root, dirs, files in os.walk(root_folder):
        num_index_html = 0
        for filename in files:
            if filename.lower() == "index.html":
                num_index_html = num_index_html + 1
        if num_index_html == 1:
            root = root[len("_output")+1:]
            if root != "404":
                matching_folders.append(root)
    return matching_folders


def generate_sitemap(base_url, folder_path):
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    all_links = find_single_index_folders(folder_path)

    for items in all_links:
        url = ET.SubElement(root, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/{items}"
        loc.text = f"{loc.text.replace(chr(92), '/')}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = get_last_modified_time(items) + "\n"

    tree = ET.ElementTree(root)
    tree.write("_output/sitemap.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    base_url = "https://example.org"
    folder_path = "_output"
    generate_sitemap(base_url, folder_path)

