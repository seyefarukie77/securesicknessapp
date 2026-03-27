terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Artifact Registry repo
resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = "app-images"
  description   = "Docker images for securesicknessapp"
  format        = "DOCKER"
}

# GKE cluster
resource "google_container_cluster" "primary" {
  name     = "securesicknessapp-cluster"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  networking_mode = "VPC_NATIVE"

  ip_allocation_policy {}

  release_channel {
    channel = "REGULAR"
  }
}

# Node pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name

  node_count = 2

  node_config {
    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}
