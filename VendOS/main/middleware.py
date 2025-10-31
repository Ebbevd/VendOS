# myapp/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings

class RestrictHostMiddleware:
    """
    Allows specific hosts or IPs to access only certain paths/methods.
    Denies everything else from those hosts.
    """

    ALLOWED_HOSTS = [settings.ALLOWED_HOSTS[-1], "wwww.ds-technical-solutions.nl"]  # or IPs like "3.90.12.45"
    ALLOWED_PATHS = ["/payments/webhook", "/status/update-status", "/status/get-status"]             # paths that host is allowed to access
    ALLOWED_METHODS = ["POST", "GET"]             

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        client_ip = request.META.get("REMOTE_ADDR")

        # Check if host/IP is the special one
        if host in self.ALLOWED_HOSTS or client_ip in self.ALLOWED_HOSTS:
            # If the request is NOT in allowed paths or methods → reject it
            if not any(request.path.startswith(p) for p in self.ALLOWED_PATHS) \
               or request.method not in self.ALLOWED_METHODS:
                return HttpResponseForbidden("This host is not allowed to access this resource")

        # Otherwise, normal flow
        return self.get_response(request)