"""Custom template tags for app"""
import re

from django import template
from django.core.urlresolvers import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, *args):
    """Place an active class for navigation buttons on appropriate urls"""
    path = context['request'].path

    try:
        for url in args:
            pattern = '^' + reverse(url) + '$'
            if re.search(pattern, path):
                return 'active'

    except NoReverseMatch:
        if len(args):
            pattern = args[0]

    if re.search(pattern, path):
        return 'active'
    return ''


@register.simple_tag(takes_context=False)
def boolean_filter(handle, *args):
    """Boolean filter to replace boolean values with words"""
    if handle is True and len(args) == 2:
        return args[0]
    else:
        return args[1]
