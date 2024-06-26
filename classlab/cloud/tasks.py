import json
import logging

from django.apps import apps
from django.http import HttpResponseForbidden
from kubernetes.client.rest import ApiException

from config import celery_app

from .managers import K8sManager
from .managers import ResourceQuota

logger = logging.getLogger(__name__)


@celery_app.task()
def create_app(app_id: str, config: dict):
    """A task that creates an app"""
    App = apps.get_model("apps", "App")

    try:
        app = App.objects.get(app_id=app_id)
        logging.info("App found: %s", app)
        manifest = app.generate_manifest(config)
        k8s = K8sManager()
        return k8s.apply_manifest(app.namespace, manifest)

    except App.DoesNotExist:
        logging.exception("App does not exist: %s", app_id)
        return None
    except ApiException as e:
        if e.status == HttpResponseForbidden.status_code:
            body = json.loads(e.body)
            message = body["message"]
            logger.warning(message)
            if "exceeded quota" in message:
                app.delete()
                return None
        app.delete()
        raise
    except Exception:
        app.delete()
        raise


@celery_app.task()
def start_app(namespace: str, app_id: str):
    """A task that starts an app"""
    App = apps.get_model("apps", "App")
    app = App.objects.get(app_id=app_id)
    manifest = app.generate_manifest()
    k8s = K8sManager()
    k8s.start_app(namespace, manifest)


@celery_app.task()
def stop_app(namespace, app_id: str):
    """A task that stops an app"""
    App = apps.get_model("apps", "App")
    app = App.objects.get(app_id=app_id)
    manifest = app.generate_manifest()
    k8s = K8sManager()
    k8s.stop_app(namespace, manifest)


@celery_app.task()
def delete_app(namespace: str, manifest: list):
    """A task that deletes an app"""
    k8s = K8sManager()
    return k8s.delete_app(namespace, manifest)


@celery_app.task()
def create_namespace(namespace: str):
    """A task that creates a namespace in k8s"""
    k8s = K8sManager()
    k8s.create_namespace(namespace)


@celery_app.task()
def set_resource_quota(namespace: str, resource_quota: dict):
    """A task that sets resource quota for a namespace"""
    rq = ResourceQuota(**resource_quota)
    k8s = K8sManager()
    k8s.set_resource_quota(namespace, rq)
