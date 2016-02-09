"""Custom tests for access control"""
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from inventory.message_constants import ALREADY_LOGGED_MESSAGE, LOGIN_REQUIRED_MESSAGE


def check_access(user, admin_prompt):
    """Function to check access level and raise 404"""

    if not user.is_authenticated():
        return False
    elif not user.is_admin == admin_prompt:
        raise Http404
    else:
        return True


def check_already_logged(f):
    """Function to check if a user is already logged in at login page"""

    def wrapper(self, request):
        if request.user.is_authenticated():
            messages.warning(request, ALREADY_LOGGED_MESSAGE)
            return HttpResponseRedirect(reverse_lazy('dashboard'))
        return f(self, request)

    return wrapper

admin_required = user_passes_test(
    lambda u: check_access(
        u, True), login_url='login')

user_required = user_passes_test(
    lambda u: check_access(
        u, False), login_url='login')
