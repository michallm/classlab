resource "helm_release" "keda" {
  name             = "keda"
  repository       = "https://kedacore.github.io/charts"
  chart            = "keda"
  version          = "2.10.2"
  namespace        = "keda"
  create_namespace = true
  force_update     = true
}
