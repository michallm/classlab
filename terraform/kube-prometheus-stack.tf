resource "helm_release" "kube-prometheus-stack" {
  depends_on = [
    null_resource.local_k8s_context,
  ]
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  version          = "46.6.0"
  namespace        = "monitoring"
  create_namespace = true

  values = [
    "${file("../infra/k8s-prod/kube-prometheus/values.yml")}"
  ]
}


resource "null_resource" "kube-prometheus-stack-middleware" {
  depends_on = [
    null_resource.local_k8s_context,
    helm_release.kube-prometheus-stack,
  ]

  provisioner "local-exec" {
    command = <<EOF
      kubectl apply -f ../infra/k8s-prod/kube-prometheus/middleware.yml
    EOF
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<EOF
      kubectl delete -f ../infra/k8s-prod/kube-prometheus/middleware.yml
    EOF
  }
}
