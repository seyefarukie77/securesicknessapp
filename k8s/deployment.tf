resource "kubernetes_deployment" "secureapp" {
  metadata {
    name = "secureapp"
    labels = {
      app = "secureapp"
    }
  }

  spec {
    replicas = 2

    strategy {
      type = "RollingUpdate"

      rolling_update {
        max_surge       = 1
        max_unavailable = 0
      }
    }

    selector {
      match_labels = {
        app = "secureapp"
      }
    }

    template {
      metadata {
        labels = {
          app = "secureapp"
        }
      }

      spec {
        container {
          name  = "secureapp"
          image = "${var.image_repo}:${var.image_tag}"

          port {
            container_port = 8080
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 10
            timeout_seconds       = 2
            failure_threshold     = 3
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8080
            }
            initial_delay_seconds = 15
            period_seconds        = 20
            timeout_seconds       = 2
            failure_threshold     = 3
          }
        }
      }
    }
  }
}