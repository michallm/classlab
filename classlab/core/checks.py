import sys

from django.conf import settings
from django.core.checks import Warning as CheckWarning


def check_dev_mode(**kwargs):
    errors = []

    if settings.DEBUG and not sys.flags.dev_mode:
        errors.append(
            CheckWarning(
                "Python development mode is not active with DEBUG.",
                hint=(
                    "Set the environment variable PYTHONDEVMODE=1 or run"
                    " with python -X dev'."
                ),
                id="classlab.W001",
            ),
        )

    return errors
