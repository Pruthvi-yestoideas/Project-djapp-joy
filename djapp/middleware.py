from djapp.plugins.Home_Page import get_balance

class UserUpdateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        user_id = request.session.get('user_auth')
        if user_id:
            request.session['balance'] = get_balance(user_id)
        return response
