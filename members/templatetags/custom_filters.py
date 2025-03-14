from django import template
import os

register = template.Library()

@register.filter
def filename(value):
    """
    Returns only the filename from a file path.
    Usage: {{ form.documents.value|filename }}
    """
    if value:
        return os.path.basename(str(value))
    return ""

@register.filter
def directory_path(value):
    """
    Returns only the directory path from a file path without the filename.
    Usage: {{ form.documents.value|directory_path }}
    """
    if value:
        path = str(value)
        directory = os.path.dirname(path)
        return directory
    return ""