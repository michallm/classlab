resource "kubernetes_service_account" "django" {
  metadata {
    name = "django"
  }
}

resource "kubernetes_cluster_role_binding" "django" {
  depends_on = [
    kubernetes_service_account.django
  ]
  metadata {
    name = "django-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  subject {
    kind      = "ServiceAccount"
    name      = "django"
    namespace = "default"
  }
}

resource "kubernetes_secret" "django" {
  depends_on = [
    kubernetes_cluster_role_binding.django
  ]
  metadata {
    name      = "django-token"
    namespace = "default"
    annotations = {
      "kubernetes.io/service-account.name" = "django"
    }
  }
  type = "kubernetes.io/service-account-token"
}

output "kubeconfig" {
  depends_on = [
    kubernetes_secret.django
  ]
  value = templatefile("${path.module}/templates/kubeconfig.yml.tpl", {
    cluster_name           = google_container_cluster.default.name
    user_name              = "django"
    cluster_ca_certificate = google_container_cluster.default.master_auth.0.cluster_ca_certificate
    endpoint               = google_container_cluster.default.endpoint
    token                  = kubernetes_secret.django.data["token"]
  })
  sensitive   = true
  description = "Kubeconfig file for the cluster"
}
