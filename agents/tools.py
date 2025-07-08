
# agent/tools.py
from lxml import html
import json

def is_xpath_present_in_dom(dom_string: str, xpath: str) -> bool:
    """
    A fast, local check to see if an XPath exists in a DOM.
    This does NOT use the LLM.
    """
    try:
        tree = html.fromstring(dom_string.encode('utf-8'))
        return len(tree.xpath(xpath)) > 0
    except Exception:
        return False