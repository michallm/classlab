resource "helm_release" "datree" {
  name             = "datree"
  repository       = "https://datreeio.github.io/admission-webhook-datree"
  chart            = "datree-admission-webhook "
  version          = "0.3.77"
  namespace        = "datree"
  create_namespace = true
  force_update     = true

  set {
    name  = "datree.token"
    value = var.datree_token
  }

  set {
    name  = "datree.clusterName"
    value = var.gke_cluster_name
  }
}
