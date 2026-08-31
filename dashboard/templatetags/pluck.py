# dashboard/templatetags/pluck.py
from django import template

register = template.Library()

@register.filter
def pluck(items, key):
    result = []
    for obj in items:
        if isinstance(obj, dict):  
            result.append(obj.get(key))
        else:  
            result.append(getattr(obj, key, None))
    return result
