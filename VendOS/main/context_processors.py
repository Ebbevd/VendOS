from django.conf import settings

def debug_flag(request):
    return {
        "DEBUG": settings.DEBUG,
        "VEND_NAME": settings.VEND_NAME
    }