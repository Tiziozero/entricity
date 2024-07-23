from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag
import bs4

class HTMLElement:
    def __init__(self, tag: str, attrs: Dict[str, str], text: str = "", children: Optional[List['HTMLElement']] = None):
        self.tag = tag
        self.attrs = attrs
        self.text = text
        self.children = children or []
    
    def prettyprint(self, indent: int = 0) -> None:
        indent_str = "  " * indent
        print(f"{indent_str}<{self.tag}>")
        if self.text:
            print(f"{indent_str}  {self.text}")
        for child in self.children:
            child.prettyprint(indent + 1)

        if self.text:
            print(f"{indent_str}{self.text}")
        print(f"{indent_str}</{self.tag}>")

    def __repr__(self):
        return f"HTMLElement(tag='{self.tag}', attrs={self.attrs}, text='{self.text}', children={self.children})"

def create_element(node: Tag) -> HTMLElement:
    attrs = {key: value for key, value in node.attrs.items()}
    text = node.get_text(strip=True) if node.string else ""
    children = [create_element(child) for child in node.find_all(recursive=False)]
    return HTMLElement(tag=node.name, attrs=attrs, text=text, children=children)

def parse_html_to_tree(html_doc: str) -> Optional[HTMLElement]:
    try:
        soup = BeautifulSoup(html_doc, 'html.parser')
        root = soup.find()
        if root is None:
            raise Exception("No root element found. The HTML might be empty or malformed.")
        if not isinstance(root, bs4.Tag):
            raise Exception(f"Root of invalid type: {type(root)}. Expected bs4.Tag.")
        return create_element(root)
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    html_doc = """
    <div class="visualMediaItemContainer_cda674">
      <div class="oneByOneGrid_cda674 oneByOneGridSingle_cda674">
        <div class="mosaicItem_e5c1dc mosaicItemNoJustify_e5c1dc mosaicItemMediaMosaic_e5c1dc hideOverflow_e5c1dc">
          <div class="imageContent_cf58b5 embedWrapper_b558d0 itemContentContainer_cda674 mosaicItemContent_e5c1dc">
            <div class="imageContainer_cf58b5">
              <div class="imageWrapper_d4597d imageZoom_d4597d clickable_d4597d lazyImgContainer_cda674" style="display: block; max-height: inherit; margin: auto; width: 424px; height: 100%;">
                <a tabindex="-1" aria-hidden="true" class="originalLink_d4597d" href="https://cdn.discordapp.com/attachments/1218150886472286300/1264607834620952626/image.png?ex=669e7d53&amp;is=669d2bd3&amp;hm=b02aed5f80639b711bf522831b6f16653e21016d7e30bdd08241f439b4de5a61&amp;" data-role="img" data-safe-src="https://media.discordapp.net/attachments/1218150886472286300/1264607834620952626/image.png?ex=669e7d53&amp;is=669d2bd3&amp;hm=b02aed5f80639b711bf522831b6f16653e21016d7e30bdd08241f439b4de5a61&amp;=&amp;format=webp&amp;quality=lossless&amp;width=424&amp;height=350"></a>
                <div class="clickableWrapper_d4597d" tabindex="0" aria-label="Image" aria-describedby="uid_4" role="button">
                  <div class="loadingOverlay_d4597d" style="aspect-ratio: 1.21143 / 1;">
                    <img class="lazyImg_cda674" alt="Image" src="https://media.discordapp.net/attachments/1218150886472286300/1264607834620952626/image.png?ex=669e7d53&amp;is=669d2bd3&amp;hm=b02aed5f80639b711bf522831b6f16653e21016d7e30bdd08241f439b4de5a61&amp;=&amp;format=webp&amp;quality=lossless&amp;width=424&amp;height=350" style="display: block; object-fit: cover; min-width: 100%; min-height: 100%; max-width: calc(100% + 1px);">
                  </div>
                </div>
              </div>
              <div class="hoverButtonGroup_e5c1dc">
                <div class="hoverButton_e5c1dc removeMosaicItemHoverButton_e5c1dc" aria-label="Remove Message Attachment" role="button" tabindex="0">
                  <svg aria-hidden="true" role="img" xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M14.25 1c.41 0 .75.34.75.75V3h5.25c.41 0 .75.34.75.75v.5c0 .41-.34.75-.75.75H3.75A.75.75 0 0 1 3 4.25v-.5c0-.41.34-.75.75-.75H9V1.75c0-.41.34-.75.75-.75h4.5Z" class=""></path>
                    <path fill="currentColor" fill-rule="evenodd" d="M5.06 7a1 1 0 0 0-1 1.06l.76 12.13a3 3 0 0 0 3 2.81h8.36a3 3 0 0 0 3-2.81l.75-12.13a1 1 0 0 0-1-1.06H5.07ZM11 12a1 1 0 1 0-2 0v6a1 1 0 1 0 2 0v-6Zm3-1a1 1 0 0 1 1 1v6a1 1 0 1 1-2 0v-6a1 1 0 0 1 1-1Z" clip-rule="evenodd" class=""></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    """

    # Parse the HTML document and create the tree
    try:
        html_tree = parse_html_to_tree(html_doc)
        if html_tree:
            html_tree.prettyprint()
    except Exception as e:
        print(f"Error: {e}")

    # Parse from file
    try:
        with open("test.html", "r") as f:
            file_content = f.read()
            print(file_content)
            parse_html_to_tree(file_content).prettyprint()
    except Exception as e:
        print(f"Error: {e}")

