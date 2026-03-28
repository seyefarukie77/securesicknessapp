resource "kubernetes_service" "secureapp" {
  metadata {
    name = "secureapp-service"
  }

  spec {
    selector = {
      app = "secureapp"
    }

    port {
      port        = 80
      target_port = 8000
    }

    type = "LoadBalancer"
  }
}
