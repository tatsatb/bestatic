import os
import datetime
import xml.etree.ElementTree as ET


def get_last_modified_time(file_path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()


def generate_sitemap(base_url, folder_path):
    root = ET.Element("urlset")
    root.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    for currpath, dirpath, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(currpath, filename)
            if currpath == folder_path:
                file_name = filename if filename != "index.html" else ""
            elif currpath == os.path.join(folder_path, "post"):
                file_name = "post" + "/" + filename
            elif currpath == os.path.join(folder_path, "post", "tags"):
                file_name = "post" + "/" + "tags" + "/" + filename
            else:
                continue

            if "index.json" in file_name or "404" in file_name or ".xml" in file_name:
                continue
            else:
                url = ET.SubElement(root, "url")
                loc = ET.SubElement(url, "loc")
                loc.text = f"{base_url}/{file_name}"
                lastmod = ET.SubElement(url, "lastmod")
                lastmod.text = get_last_modified_time(file_path)

            # ET.SubElement(url, "newline")

    tree = ET.ElementTree(root)
    tree.write("_output/sitemap.xml", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    base_url = "https://example.org"
    folder_path = "_output"
    generate_sitemap(base_url, folder_path)

