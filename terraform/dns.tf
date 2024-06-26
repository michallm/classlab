resource "google_dns_managed_zone" "default" {
  project     = var.project_id
  name        = "classlab-apps"
  dns_name    = var.domain_name
  description = "Apps DNS zone"

}

# output name_servers
output "name_servers" {
  value = google_dns_managed_zone.default.name_servers
}

resource "google_dns_record_set" "classlab-lb" {
  depends_on = [
    google_compute_address.public_ip
  ]
  project      = var.project_id
  name         = "*.${var.domain_name}"
  type         = "A"
  ttl          = 300
  managed_zone = google_dns_managed_zone.default.name
  rrdatas      = [google_compute_address.public_ip.address]
}
