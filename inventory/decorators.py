"""Custom tests for access control"""
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404


def check_access(user, admin_prompt):
    """Function to check access level and raise 404"""

    if not user.is_authenticated():
        return False
    elif not user.is_admin == admin_prompt:
        raise Http404
    else:
        return True


admin_required = user_passes_test(
    lambda u: check_access(
        u, True), login_url='login')

user_required = user_passes_test(
    lambda u: check_access(
        u, False), login_url='login')
