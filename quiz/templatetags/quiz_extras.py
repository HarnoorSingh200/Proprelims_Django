from django import template
import re

register = template.Library()


@register.filter
def strip_markdown(text):
    """
    Removes basic Markdown syntax from text.
    Not perfect, but handles common cases.
    """
    # Remove headings, bold, italic, links, images, blockquotes, code blocks
    text = re.sub(r'(?m)^#{1,6}\s+', '', text)  # Headings
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # Bold
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)  # Italic
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # Images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text)  # Inline/code blocks
    text = re.sub(r'>+\s?', '', text)  # Blockquotes
    text = re.sub(r'[-*+]\s+', '', text)  # Lists
    return text


@register.filter
def dict_get(dictionary, key):
    """Get value from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def div(value, arg):
    """Divide value by arg and return integer result"""
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mod(value, arg):
    """Return value modulo arg"""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0
