variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "able-cogency-250511"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "europe-west1-b"
}

variable "image_repo" {
  description = "Artifact Registry image repository"
  type        = string
}

variable "image_tag" {
  description = "Container image tag to deploy"
  type        = string
}
