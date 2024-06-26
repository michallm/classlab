resource "kubernetes_manifest" "external_dns_namespace" {
  depends_on = [
    null_resource.local_k8s_context,
  ]

  manifest = yamldecode(file("../infra/k8s-prod/external-dns/namespace.yml"))

}

resource "null_resource" "external_dns" {
  depends_on = [
    null_resource.local_k8s_context,
    module.external-dns-workload-identity,
  ]

  provisioner "local-exec" {
    command = "kubectl apply -f ../infra/k8s-prod/external-dns/external-dns.yml"
  }
}
