terraform {
  cloud {
    organization = "ClassLab"
    workspaces {
      name = "classlab"
    }
  }

  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "4.62.1"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.10.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.21.1"
    }
  }
}
