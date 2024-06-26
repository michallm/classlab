provider "google-beta" {
  project = var.project_id
  region  = var.region
}

resource "google_compute_subnetwork" "default" {
  depends_on    = [google_compute_network.default]
  name          = "${var.gke_cluster_name}-subnet"
  project       = google_compute_network.default.project
  region        = var.region
  network       = google_compute_network.default.name
  ip_cidr_range = "10.0.0.0/16"
}

# public standard cluster with separatly defined node pools: 1. default-pool, 2. spot-pool
resource "google_container_cluster" "default" {
  provider                 = google-beta
  project                  = var.project_id
  name                     = var.gke_cluster_name
  location                 = var.zone
  remove_default_node_pool = true
  initial_node_count       = var.num_nodes
  network                  = google_compute_network.default.name
  subnetwork               = google_compute_subnetwork.default.name
  datapath_provider        = "ADVANCED_DATAPATH"
  networking_mode          = "VPC_NATIVE"
  logging_service          = "none"
  min_master_version       = "1.26.3-gke.1000"

  cost_management_config {
    enabled = true
  }
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "10.1.0.0/16"
    services_ipv4_cidr_block = "10.2.0.0/16"
  }

  addons_config {
    http_load_balancing {
      disabled = true
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  master_authorized_networks_config {
    gcp_public_cidrs_access_enabled = true
    cidr_blocks {
      cidr_block   = "127.0.0.1/32"
      display_name = "Test"
    }

  }
  cluster_autoscaling {
    autoscaling_profile = "OPTIMIZE_UTILIZATION"
  }
}

resource "google_container_node_pool" "default" {
  name               = "default-pool"
  location           = var.zone
  cluster            = google_container_cluster.default.name
  initial_node_count = var.num_nodes
  project            = var.project_id

  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }

  node_config {
    machine_type = var.machine_type
    spot         = true
    metadata = {
      disable-legacy-endpoints = "true"
    }
    tags         = ["${var.gke_cluster_name}"]
    disk_size_gb = var.disk_size
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

resource "google_container_node_pool" "spot" {
  provider   = google-beta
  name       = "spot-pool"
  location   = var.zone
  cluster    = google_container_cluster.default.name
  node_count = var.spot_num_nodes
  project    = var.project_id

  autoscaling {
    min_node_count = 0
    max_node_count = 3
  }

  node_config {
    machine_type = var.spot_machine_type
    disk_size_gb = var.spot_disk_size
    image_type   = "COS_CONTAINERD"
    spot         = true
    taint = [
      {
        key    = "spot"
        value  = "true"
        effect = "NO_SCHEDULE"
      },
    ]
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
    metadata = {
      disable-legacy-endpoints = "true"
    }

  }
}

resource "google_compute_firewall" "node_port_access" {
  name    = "node-port-access"
  network = google_compute_network.default.name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["30000-32767"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "time_sleep" "wait_for_kube" {
  depends_on = [google_container_cluster.default, google_container_node_pool.default]
  # GKE master endpoint may not be immediately accessible, resulting in error, waiting does the trick
  create_duration = "30s"
}

resource "null_resource" "local_k8s_context" {
  depends_on = [time_sleep.wait_for_kube]
  provisioner "local-exec" {
    # Update your local gcloud and kubectl credentials for the newly created cluster
    command = "for i in 1 2 3 4 5; do gcloud container clusters get-credentials ${var.gke_cluster_name} --project=${var.project_id} --zone=${var.zone} && break || sleep 60; done"
  }
}
