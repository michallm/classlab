from django.conf import settings


def sentry(request):
    return {
        "SENTRY_DSN": getattr(settings, "SENTRY_DSN", None),
        "SENTRY_ENVIRONMENT": getattr(settings, "SENTRY_ENVIRONMENT", None),
    }
