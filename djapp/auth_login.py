from urllib.parse import urlparse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
from django.conf import settings
from django.shortcuts import redirect, reverse

from .plugins.login import maintenance_website


def login_redirect(function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    def wrapper(request):
        if not request.session.get('user_auth'):
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        else:
            if not maintenance_website():
                return redirect(reverse('djapp:maintain'))

            if not request.session.get('is_default_address') and request.path not in ["", "/", "/settings/add-default-address/"]:
                return redirect(reverse('djapp:dashboard'))
            return function(request)
    return wrapper

from functools import wraps

# Custom decorator to ensure verifypassword_views is accessible only through forgotpassword_views
def require_forgotpassword_access(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'email_forget_pass' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the forgotpassword_views if session data is not available
            return redirect('djapp:forgotpassword')

    return _wrapped_view
