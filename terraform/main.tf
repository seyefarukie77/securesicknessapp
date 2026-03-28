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

# Artifact Registry (existing)
resource "google_artifact_registry_repository" "app_images" {
  location      = var.region
  repository_id = "app-images"
  format        = "DOCKER"

  # Keep description to avoid Terraform removing it
  description = "App images"
}

# GKE Cluster (existing)
resource "google_container_cluster" "gke" {
  name     = "my-gke-cluster"
  location = var.zone

  # DO NOT set initial_node_count for imported clusters
  # DO NOT set remove_default_node_pool
  # DO NOT set addons_config, logging_config, monitoring_config, etc.

  networking_mode = "VPC_NATIVE"

  # Use empty block to match existing cluster
  ip_allocation_policy {}

  # Match real cluster network
  network    = "default"
  subnetwork = "default"

  # Prevent Terraform from trying to recreate cluster
  lifecycle {
    ignore_changes = [
      node_config,
      node_pool,
      addons_config,
      logging_config,
      monitoring_config,
      master_auth,
      cluster_autoscaling,
      resource_labels,
      authenticator_groups_config,
      gateway_api_config,
      identity_service_config,
      mesh_certificates,
      monitoring_config,
      tpu_config,
      database_encryption,
      default_snat_status,
      enable_intranode_visibility,
      enable_tpu,
      enable_autopilot,
      logging_service,
      monitoring_service,
      node_locations,
      node_version,
      master_version,
      ip_allocation_policy,
    ]
  }
}

# Node Pool (existing)
resource "google_container_node_pool" "primary_nodes" {
  name     = "default-pool"
  location = var.zone
  cluster  = google_container_cluster.gke.name

  node_count = 3

  node_config {
    machine_type = "e2-medium"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  lifecycle {
    ignore_changes = [
      node_config,
      version,
      upgrade_settings,
      management,
    ]
  }
}
