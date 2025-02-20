from django import template
import calendar
register = template.Library()
@register.filter
def to(value, arg):
    """Generate a range of numbers from value to arg (inclusive)"""
    try:
        value = int(value)
        arg = int(arg)
        return range(value, arg + 1)
    except (ValueError, TypeError):
        return []

@register.filter
def range_filter(value):
    return range(value)

@register.filter
def month_name(month_number):
    try:
        return calendar.month_name[int(month_number)]
    except (ValueError, IndexError):
        return ''


@register.filter
def split(value, delimiter=','):
    """Split a string into a list using the specified delimiter"""
    return value.split(delimiter)

@register.filter
def between(value, args):
    """
    Check if a value is between two numbers (inclusive)
    Usage: {{ value|between:start:end }}
    """
    try:
        start, end = args.split(':')
        value = int(value)
        start = int(start)
        end = int(end)
        if start <= end:
            return start <= value <= end
        else:
            return start >= value >= end
    except (ValueError, AttributeError):
        return False