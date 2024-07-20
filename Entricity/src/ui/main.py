from bs4 import BeautifulSoup
from typing import List, Optional

class HTMLElement:
    def __init__(self, tag: str, attrs: dict, children: Optional[List['HTMLElement']] = None):
        self.tag = tag
        self.attrs = attrs
        self.children = children or []

    def __repr__(self):
        return f"HTMLElement(tag='{self.tag}', attrs={self.attrs}, children={self.children})"

def parse_html_to_tree(html_doc: str) -> HTMLElement:
    def create_element(node) -> HTMLElement:
        attrs = node.attrs
        children = [create_element(child) for child in node.find_all(recursive=False)]
        return HTMLElement(tag=node.name, attrs=attrs, children=children)

    soup = BeautifulSoup(html_doc, 'lxml')
    return create_element(soup.find())

# Example usage
html_doc = """
<!DOCTYPE html>
<html>
<head>
    <title>Example Page</title>
</head>
<body>
    <h1>Main Title</h1>
    <p class="description" id="desc1">This is a description.</p>
    <p class="content" id="content1">This is some content.</p>
    <a href="http://example.com" id="link1">Visit Example.com</a>
</body>
</html>
"""

tree = parse_html_to_tree(html_doc)
print(tree)

