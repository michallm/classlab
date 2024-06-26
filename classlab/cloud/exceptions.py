class CloudConnectionError(Exception):
    """Raised when there is an error connecting to the Kubernetes API"""


class CloudResourceNotFoundError(Exception):
    """Raised when a resource is not found in Kubernetes"""
