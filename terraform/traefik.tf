resource "helm_release" "traefik" {
  depends_on = [
    null_resource.local_k8s_context,
    helm_release.kube-prometheus-stack,
  ]
  name             = "traefik"
  repository       = "https://helm.traefik.io/traefik"
  chart            = "traefik"
  version          = "23.0.1"
  namespace        = "traefik"
  create_namespace = true

  values = [
    "${file("../infra/k8s-prod/traefik/values.yml")}"
  ]

  set {
    name  = "service.spec.loadBalancerIP"
    value = google_compute_address.public_ip.address
  }
}

resource "kubernetes_manifest" "traefik-default-ssl" {
  depends_on = [
    helm_release.traefik,
    kubernetes_manifest.classlab_wildcard_cert
  ]
  manifest = yamldecode(file("../infra/k8s-prod/traefik/default-ssl.yml"))
}
