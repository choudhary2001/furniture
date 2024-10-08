from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def floatdiv(value, arg):
    try:
        return float(value) / float(arg)
    except (TypeError, ZeroDivisionError):
        return 0
    
@register.filter
def split_string(value, delimiter):
    if value:
        return value.split(delimiter)
    else:
        return []