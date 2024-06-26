import enum
from dataclasses import dataclass

import kubernetes
from django.http import HttpResponseNotFound
from django.utils.translation import gettext_lazy as _

KUBERNETES_TIMEOUT = 3


class Kind(enum.Enum):
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    CONFIGMAP = "configmap"
    SERVICE = "service"
    SECRET = "secret"  # noqa: S105
    PERSISTENTVOLUMECLAIM = "persistentvolumeclaim"
    HORIZONTALPODAUTOSCALER = "horizontalpodautoscaler"
    NETWORKPOLICY = "networkpolicy"
    SCALEDOBJECT = "scaledobject"
    INGRESSROUTE = "ingressroute"
    INGRESS = "ingress"


class AppStatus(enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    CREATING = "creating"
    DELETING = "deleting"
    ERROR = "error"

    # versbose names
    @property
    def verbose_name(self):
        return {
            AppStatus.RUNNING: _("Running"),
            AppStatus.STOPPED: _("Stopped"),
            AppStatus.STARTING: _("Starting"),
            AppStatus.STOPPING: _("Stopping"),
            AppStatus.CREATING: _("Creating"),
            AppStatus.DELETING: _("Deleting"),
            AppStatus.ERROR: _("Error"),
        }[self]


@dataclass
class K8sResource:
    manifest: dict
    custom = False


@dataclass
class Deployment(K8sResource):
    kind: Kind = Kind.DEPLOYMENT
    api = kubernetes.client.AppsV1Api
    create_method = "create_namespaced_deployment"
    delete_method = "delete_namespaced_deployment"
    read_method = "read_namespaced_deployment"
    patch_method = "patch_namespaced_deployment"


@dataclass
class StatefulSet(K8sResource):
    kind: Kind = Kind.STATEFULSET
    api = kubernetes.client.AppsV1Api
    create_method = "create_namespaced_stateful_set"
    delete_method = "delete_namespaced_stateful_set"
    read_method = "read_namespaced_stateful_set"
    patch_method = "patch_namespaced_stateful_set"

    # template-app_id
    name = "{}-{}"


@dataclass
class ConfigMap(K8sResource):
    kind: Kind = Kind.CONFIGMAP
    api = kubernetes.client.CoreV1Api
    create_method = "create_namespaced_config_map"
    delete_method = "delete_namespaced_config_map"
    read_method = "read_namespaced_config_map"
    patch_method = "patch_namespaced_config_map"


@dataclass
class Service(K8sResource):
    kind: Kind = Kind.SERVICE
    api = kubernetes.client.CoreV1Api
    create_method = "create_namespaced_service"
    delete_method = "delete_namespaced_service"
    read_method = "read_namespaced_service"
    patch_method = "patch_namespaced_service"


@dataclass
class PersistentVolumeClaim(K8sResource):
    kind: Kind = Kind.PERSISTENTVOLUMECLAIM
    api = kubernetes.client.CoreV1Api
    create_method = "create_namespaced_persistent_volume_claim"
    delete_method = "delete_namespaced_persistent_volume_claim"
    read_method = "read_namespaced_persistent_volume_claim"
    patch_method = "patch_namespaced_persistent_volume_claim"


@dataclass
class HorizontalPodAutoscaler(K8sResource):
    kind: Kind = Kind.HORIZONTALPODAUTOSCALER
    api = kubernetes.client.AutoscalingV2Api
    create_method = "create_namespaced_horizontal_pod_autoscaler"
    delete_method = "delete_namespaced_horizontal_pod_autoscaler"
    read_method = "read_namespaced_horizontal_pod_autoscaler"
    patch_method = "patch_namespaced_horizontal_pod_autoscaler"


@dataclass
class Secret(K8sResource):
    kind: Kind = Kind.SECRET
    api = kubernetes.client.CoreV1Api
    create_method = "create_namespaced_secret"
    delete_method = "delete_namespaced_secret"
    read_method = "read_namespaced_secret"
    patch_method = "patch_namespaced_secret"


@dataclass()
class Ingress(K8sResource):
    """K8s Ingress resource"""

    kind = Kind.INGRESS
    api = kubernetes.client.NetworkingV1Api
    create_method = "create_namespaced_ingress"
    delete_method = "delete_namespaced_ingress"
    read_method = "read_namespaced_ingress"
    patch_method = "patch_namespaced_ingress"


@dataclass
class NetworkPolicy(K8sResource):
    kind: Kind = Kind.NETWORKPOLICY
    api = kubernetes.client.NetworkingV1Api
    create_method = "create_namespaced_network_policy"
    delete_method = "delete_namespaced_network_policy"
    read_method = "read_namespaced_network_policy"
    patch_method = "patch_namespaced_network_policy"


@dataclass
class ScaledObject(K8sResource):
    kind: Kind = Kind.SCALEDOBJECT
    api = kubernetes.client.CustomObjectsApi
    create_method = "create_namespaced_custom_object"
    delete_method = "delete_namespaced_custom_object"
    read_method = "get_namespaced_custom_object"
    patch_method = "patch_namespaced_custom_object"
    custom = True
    group = "keda.sh"
    version = "v1alpha1"
    plural = "scaledobjects"


@dataclass
class IngressRoute(K8sResource):
    """Traefik IngressRoute resource"""

    kind = Kind.INGRESSROUTE
    api = kubernetes.client.CustomObjectsApi
    create_method = "create_namespaced_custom_object"
    delete_method = "delete_namespaced_custom_object"
    read_method = "get_namespaced_custom_object"
    patch_method = "patch_namespaced_custom_object"
    custom = True
    group = "traefik.containo.us"
    version = "v1alpha1"
    plural = "ingressroutes"


K8S_RESOURCES = {
    Kind.DEPLOYMENT.value: Deployment,
    Kind.STATEFULSET.value: StatefulSet,
    Kind.CONFIGMAP.value: ConfigMap,
    Kind.SERVICE.value: Service,
    Kind.SECRET.value: Secret,
    Kind.PERSISTENTVOLUMECLAIM.value: PersistentVolumeClaim,
    Kind.NETWORKPOLICY.value: NetworkPolicy,
    Kind.INGRESS.value: Ingress,
    Kind.HORIZONTALPODAUTOSCALER.value: HorizontalPodAutoscaler,
    Kind.SCALEDOBJECT.value: ScaledObject,
    Kind.INGRESSROUTE.value: IngressRoute,
}


@dataclass
class ResourceQuota:
    cpu: int
    memory: int
    storage: int


class K8sManager:
    def __init__(self):
        self._load_local_configuration()
        self.api_client = kubernetes.client.ApiClient()
        self.client = kubernetes.client

    def _load_local_configuration(self):
        # try load in-cluster configuration
        kubernetes.config.load_kube_config()

    def _get_resource(self, resource: dict) -> K8sResource:
        kind = resource["kind"].lower()
        if kind not in K8S_RESOURCES:
            raise ValueError(_("Unsupported resource kind: {kind}").format(kind=kind))
        return K8S_RESOURCES[kind](manifest=resource)

    def request(self, resource, method, *args, **kwargs):
        return getattr(resource.api(), method)(
            *args,
            **kwargs,
            _request_timeout=KUBERNETES_TIMEOUT,
        )

    def apply_resource(self, namespace: str, resource: K8sResource) -> dict:
        """Apply a resource to k8s

        It works like `kubectl apply -f <resource>`
        """

        try:
            if resource.custom is True:
                resp = self.request(
                    resource,
                    resource.read_method,
                    group=resource.group,
                    version=resource.version,
                    namespace=namespace,
                    plural=resource.plural,
                    name=resource.manifest["metadata"]["name"],
                )

            else:
                resp = self.request(
                    resource,
                    resource.read_method,
                    name=resource.manifest["metadata"]["name"],
                    namespace=namespace,
                )
        except kubernetes.client.rest.ApiException as e:
            if e.status == HttpResponseNotFound.status_code:
                resp = None
            else:
                raise

        if resp is None:
            if resource.custom is True:
                resp = self.request(
                    resource,
                    resource.create_method,
                    group=resource.group,
                    version=resource.version,
                    namespace=namespace,
                    plural=resource.plural,
                    body=resource.manifest,
                )
            else:
                resp = self.request(
                    resource,
                    resource.create_method,
                    namespace=namespace,
                    body=resource.manifest,
                )
        elif resource.custom:
            resp = self.request(
                resource,
                resource.patch_method,
                group=resource.group,
                version=resource.version,
                namespace=namespace,
                plural=resource.plural,
                name=resource.manifest["metadata"]["name"],
                body=resource.manifest,
            )
        else:
            resp = self.request(
                resource,
                resource.patch_method,
                name=resource.manifest["metadata"]["name"],
                namespace=namespace,
                body=resource.manifest,
            )

        if resource.custom:
            return resp

        return resp.to_dict()

    def apply_manifest(self, namespace: str, manifest: list):
        """Apply a manifest to k8s

        It works like `kubectl apply -f <manifest>`
        """
        responses = {}
        for resource_manifest in manifest:
            resource = self._get_resource(resource_manifest)
            response = self.apply_resource(namespace, resource)
            responses[resource.kind.value] = response

        return responses

    def scale_app(self, namespace: str, manifest: list, replicas: int):
        """Scale an app setting the replicas"""
        scalable_resources = [
            Kind.DEPLOYMENT.value,
            Kind.STATEFULSET.value,
        ]

        for resource_manifest in manifest:
            resource = self._get_resource(resource_manifest)
            if resource.kind.value not in scalable_resources:
                continue
            resource.manifest["spec"]["replicas"] = replicas
            self.apply_resource(namespace, resource)

    def delete_app(self, namespace: str, manifest: list):
        """Delete an app"""
        for resource_manifest in manifest:
            resource = self._get_resource(resource_manifest)
            try:
                if resource.custom is True:
                    self.request(
                        resource,
                        resource.delete_method,
                        group=resource.group,
                        version=resource.version,
                        namespace=namespace,
                        plural=resource.plural,
                        name=resource.manifest["metadata"]["name"],
                    )
                else:
                    self.request(
                        resource,
                        resource.delete_method,
                        name=resource.manifest["metadata"]["name"],
                        namespace=namespace,
                    )
            except kubernetes.client.rest.ApiException as e:
                if e.status == HttpResponseNotFound.status_code:
                    pass
                else:
                    raise

    def stop_app(self, namespace: str, manifest: list):
        """Stop an app setting the replicas to 0"""
        self.scale_app(namespace, manifest, 0)

    def start_app(self, namespace: str, manifest: list):
        """Start an app setting the replicas to 1"""
        self.scale_app(namespace, manifest, 1)

    def create_namespace(self, namespace: str):
        """Create a namespace in k8s"""
        body = self.client.V1Namespace(
            metadata=self.client.V1ObjectMeta(
                name=namespace,
                labels={"security.kubernetes.io/warn": "restricted"},
            ),
        )
        self.client.CoreV1Api().create_namespace(
            body=body,
            _request_timeout=KUBERNETES_TIMEOUT,
        )

    # TODO: simplify this method
    def get_app_status(self, namespace: str, manifest: list) -> AppStatus:  # noqa: C901, PLR0912
        """Get the status of a resource"""

        scalable_resources = [
            Kind.DEPLOYMENT.value,
            Kind.STATEFULSET.value,
        ]

        status_response = {}

        for resource_manifest in manifest:
            resource = self._get_resource(resource_manifest)
            if resource.kind.value not in scalable_resources:
                continue
            try:
                if resource.custom is True:
                    resp = self.request(
                        resource,
                        resource.read_method,
                        group=resource.group,
                        version=resource.version,
                        namespace=namespace,
                        plural=resource.plural,
                        name=resource.manifest["metadata"]["name"],
                    )
                else:
                    resp = self.request(
                        resource,
                        resource.read_method,
                        name=resource.manifest["metadata"]["name"],
                        namespace=namespace,
                    )

                status_response[resource.kind.value] = resp.to_dict()["status"]

            except kubernetes.client.rest.ApiException as e:
                if e.status == HttpResponseNotFound.status_code:
                    resp = None
                else:
                    raise

        matched_status = 0
        for resource in status_response:
            if (
                status_response[resource].get("ready_replicas", 0) == 1
                and status_response[resource].get("replicas", 0) == 1
                and status_response[resource].get("available_replicas", 0) == 1
            ):
                matched_status += 1
        if matched_status == len(status_response):
            return AppStatus.RUNNING

        matched_status = 0
        for resource in status_response:
            if (
                status_response[resource].get("replicas", 0) == 1
                and status_response[resource].get("unavailable_replicas", 0) == 1
            ):
                matched_status += 1
        if matched_status == len(status_response):
            return AppStatus.STARTING

        # if any of the resources have number of replicas 1 and ready_replicas 0, then
        # the app is starting
        matched_status = 0
        for resource in status_response:
            if status_response[resource].get("ready_replicas", None) is None:
                matched_status += 1
        if matched_status == len(status_response):
            return AppStatus.STOPPED

        # if nothing matches, then the app is in error state
        return AppStatus.ERROR

    def get_app_node_port(self, namespace: str, manifest: list) -> int:
        """Get the node port of a service"""
        for resource_manifest in manifest:
            resource = self._get_resource(resource_manifest)
            if resource.kind.value != Kind.SERVICE.value:
                continue
            try:
                resp = self.request(
                    resource,
                    resource.read_method,
                    name=resource.manifest["metadata"]["name"],
                    namespace=namespace,
                )
                return resp.to_dict()["spec"]["ports"][0]["node_port"]

            except kubernetes.client.rest.ApiException as e:
                if e.status == HttpResponseNotFound.status_code:
                    resp = None
                else:
                    raise

        return None

    def get_secret(self, namespace: str, secret_name: str) -> dict:
        """Get the secret"""
        try:
            resp = self.client.CoreV1Api().read_namespaced_secret(
                name=secret_name,
                namespace=namespace,
            )
            return resp.to_dict()

        except kubernetes.client.rest.ApiException as e:
            if e.status == HttpResponseNotFound.status_code:
                resp = None
            else:
                raise

        return None

    def set_resource_quota(self, namespace: str, resource_quota: ResourceQuota):
        """Set the resource quota for a namespace"""
        # get resource quota if exists
        try:
            resp = self.client.CoreV1Api().read_namespaced_resource_quota(
                name=namespace,
                namespace=namespace,
            )

            # update resource quota
            resp.spec.hard["limits.cpu"] = resource_quota.cpu
            resp.spec.hard["limits.memory"] = f"{resource_quota.memory}Mi"
            resp.spec.hard["requests.storage"] = f"{resource_quota.storage}Gi"

            # apply resource quota
            self.client.CoreV1Api().patch_namespaced_resource_quota(
                name=namespace,
                namespace=namespace,
                body=resp,
            )

        except kubernetes.client.rest.ApiException as e:
            if e.status == HttpResponseNotFound.status_code:
                # create resource quota
                body = self.client.V1ResourceQuota(
                    metadata=self.client.V1ObjectMeta(name=namespace),
                    spec=self.client.V1ResourceQuotaSpec(
                        hard={
                            "limits.cpu": resource_quota.cpu,
                            "limits.memory": f"{resource_quota.memory}Mi",
                            "requests.storage": f"{resource_quota.storage}Gi",
                        },
                    ),
                )
                self.client.CoreV1Api().create_namespaced_resource_quota(
                    namespace=namespace,
                    body=body,
                )
            else:
                raise

    def test_connection(self):
        """Test connection to k8s"""
        self.client.CoreV1Api().list_namespace()
