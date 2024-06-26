resource "google_service_account" "external-dns-sa" {
  account_id   = "external-dns"
  display_name = "External DNS Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "external-dns-binding" {
  depends_on = [google_service_account.external-dns-sa]
  project    = var.project_id
  role       = "roles/dns.admin"
  member     = "serviceAccount:${google_service_account.external-dns-sa.email}"
}

module "external-dns-workload-identity" {
  depends_on = [
    google_project_iam_member.external-dns-binding,
    kubernetes_manifest.external_dns_namespace
  ]
  source                          = "terraform-google-modules/kubernetes-engine/google//modules/workload-identity"
  name                            = google_service_account.external-dns-sa.account_id
  namespace                       = "external-dns"
  project_id                      = var.project_id
  use_existing_gcp_sa             = true
  k8s_sa_name                     = "external-dns"
  automount_service_account_token = true
}

resource "google_service_account" "dns01-solver" {
  account_id   = "dns01-solver"
  display_name = "DNS01 Solver Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "dns01-solver-binding" {
  depends_on = [google_service_account.dns01-solver]
  project    = var.project_id
  role       = "roles/dns.admin"
  member     = "serviceAccount:${google_service_account.dns01-solver.email}"
}

module "cert-manager_workload-identity" {
  depends_on = [
    kubernetes_manifest.cert_manager_namespace,
    helm_release.cert_manager,
  ]
  source              = "terraform-google-modules/kubernetes-engine/google//modules/workload-identity"
  version             = "26.1.1"
  name                = "cert-manager"
  namespace           = "cert-manager"
  project_id          = var.project_id
  use_existing_gcp_sa = true
  gcp_sa_name         = "dns01-solver"
  use_existing_k8s_sa = true
  annotate_k8s_sa     = false
}

# annotate k8s sa
resource "null_resource" "annotate_k8s_sa" {
  depends_on = [
    module.cert-manager_workload-identity,
  ]
  provisioner "local-exec" {
    command = "kubectl annotate serviceaccount -n cert-manager cert-manager iam.gke.io/gcp-service-account=${google_service_account.dns01-solver.email}"
  }
}
