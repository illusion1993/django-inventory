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


@register.simple_tag(takes_context=True)
def role_prefix(context, *args):
    """Place an active class for navigation buttons on appropriate urls"""
    user = context['request'].user
    user_role = context['request'].GET.get('user', False)
    path = context['request'].path

    if path == reverse('dashboard'):
        if user.is_admin and not user_role:
            return args[0]

        elif user.is_admin and user_role:
            return args[1]

    else:
        return ''