# monitoring policies - "../infra/k8s-prod/policies/monitoring"
# policies - "../infra/k8s-prod/policies"

resource "null_resource" "network_policies" {
  depends_on = [
    null_resource.local_k8s_context
  ]

  provisioner "local-exec" {
    command = "kubectl apply -f ../infra/k8s-prod/policies"
  }
  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ../infra/k8s-prod/policies"
  }
}

resource "null_resource" "monitoring_policies" {
  depends_on = [
    null_resource.local_k8s_context
  ]

  provisioner "local-exec" {
    command = "kubectl apply -f ../infra/k8s-prod/policies/monitoring"
  }
  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ../infra/k8s-prod/policies/monitoring"
  }
}
