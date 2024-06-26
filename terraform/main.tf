

variable "project_id" {
  description = "The project ID to host the cluster in"
}

variable "region" {
  description = "The region to host the cluster in"
}

variable "zone" {
  description = "The zone to host the cluster in (required if is a zonal cluster)"
}

variable "network_name" {
  description = "The name of the network"
}

variable "gke_cluster_name" {
  description = "The name of the cluster"
}

variable "num_nodes" {
  description = "The number of cluster nodes"
}

variable "spot_num_nodes" {
  description = "The number of cluster nodes in the spot pool"

}

variable "machine_type" {
  description = "The machine type of the cluster nodes"
}

variable "spot_machine_type" {
  description = "The machine type of the cluster nodes in the spot pool"
}

variable "disk_size" {
  description = "The disk size of the cluster nodes"
}

variable "spot_disk_size" {
  description = "The disk size of the cluster nodes in the spot pool"
}

variable "ip_address_name" {
  description = "The name of the static IP Address for the load balancer"
}

variable "ssl_cert_name" {
  description = "The name of the SSL certificate for the load balancer"
}

variable "domain_name" {
  description = "The domain name for the ssl certificate"
}

variable "datree_token" {
  description = "The datree token"
}

resource "google_compute_network" "default" {
  name                    = var.network_name
  auto_create_subnetworks = "false"
  project                 = var.project_id
  # Everything in this solution is deployed regionally
  routing_mode = "REGIONAL"
}


resource "google_compute_project_default_network_tier" "default" {
  project      = var.project_id
  network_tier = "PREMIUM"
}

resource "google_compute_address" "public_ip" {
  name         = "public-ip"
  address_type = "EXTERNAL"
  project      = var.project_id
  region       = var.region
}

provider "helm" {
  registry_config_path = "repositories.yaml"
  kubernetes {
    config_path = "~/.kube/config"
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}
