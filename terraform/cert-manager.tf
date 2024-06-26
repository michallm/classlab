resource "kubernetes_manifest" "cert_manager_namespace" {
  depends_on = [
    null_resource.local_k8s_context,
  ]

  manifest = yamldecode(file("../infra/k8s-prod/cert-manager/namespace.yml"))
}

resource "helm_release" "cert_manager" {
  depends_on = [
    null_resource.local_k8s_context,
  ]
  chart            = "cert-manager"
  repository       = "https://charts.jetstack.io"
  name             = "cert-manager"
  version          = "v1.11.0"
  namespace        = "cert-manager"
  create_namespace = false

  set {
    name  = "installCRDs"
    value = "true"
  }

  set {
    name  = "startupapicheck.enabled"
    value = "false"
  }
}

resource "kubernetes_manifest" "cluster_issuer" {
  depends_on = [
    null_resource.local_k8s_context,
    helm_release.cert_manager
  ]

  manifest = yamldecode(file("../infra/k8s-prod/cert-manager/letsencrypt-production.yml"))
}

resource "kubernetes_manifest" "classlab_wildcard_cert" {
  depends_on = [
    null_resource.local_k8s_context,
    helm_release.cert_manager
  ]

  manifest = yamldecode(file("../infra/k8s-prod/cert-manager/classlab-apps-wildcard-cert.yml"))
}

resource "kubernetes_manifest" "letsencrypt_prod" {
  depends_on = [
    null_resource.local_k8s_context,
    helm_release.cert_manager
  ]

  manifest = yamldecode(file("../infra/k8s-prod/cert-manager/letsencrypt-prod.yml"))
}
